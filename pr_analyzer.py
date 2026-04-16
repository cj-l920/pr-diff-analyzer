#!/usr/bin/env python3
"""
PR Diff Analysis Agent
A tool for analyzing GitHub Pull Request diffs using AI-powered code review.

Author: Atlas (Bounty Hunter)
License: MIT
"""

import os
import sys
import json
import argparse
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import requests


@dataclass
class AnalysisResult:
    """Container for PR analysis results."""
    pr_number: int
    pr_title: str
    author: str
    summary: str
    files_changed: int
    additions: int
    deletions: int
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    security_concerns: List[str]
    test_coverage: Dict[str, Any]
    breaking_changes: List[str]
    timestamp: str


class GitHubAPI:
    """GitHub API client for fetching PR data."""
    
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_pr(self, owner: str, repo: str, pr_number: int) -> Dict:
        """Fetch PR details."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch PR diff as raw text."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {**self.headers, "Accept": "application/vnd.github.v3.diff"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    
    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch list of changed files in PR."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        files = []
        page = 1
        
        while True:
            response = requests.get(
                url, 
                headers=self.headers, 
                params={"page": page, "per_page": 100}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            files.extend(data)
            page += 1
        
        return files
    
    def post_comment(self, owner: str, repo: str, pr_number: int, body: str) -> Dict:
        """Post a comment on the PR."""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        response = requests.post(
            url, 
            headers=self.headers, 
            json={"body": body}
        )
        response.raise_for_status()
        return response.json()


class DiffAnalyzer:
    """Analyzes PR diffs for various patterns and issues."""
    
    # Security patterns to detect
    SECURITY_PATTERNS = {
        "hardcoded_secret": re.compile(
            r'(password|secret|token|key|api_key)\s*=\s*["\'][^"\']{8,}["\']',
            re.IGNORECASE
        ),
        "sql_injection": re.compile(
            r'(execute|query|raw)\s*\(.*["\'].*\$\{.*\}.*["\']',
            re.IGNORECASE
        ),
        "eval_usage": re.compile(r'\beval\s*\(', re.IGNORECASE),
        "dangerous_deserialization": re.compile(
            r'(pickle\.loads|yaml\.load|unserialize)\s*\(',
            re.IGNORECASE
        ),
        "insecure_http": re.compile(r'http://[^\s\"\']+', re.IGNORECASE),
    }
    
    # Breaking change indicators
    BREAKING_CHANGE_PATTERNS = {
        "function_removal": re.compile(r'^-\s*def\s+\w+\s*\(', re.MULTILINE),
        "class_removal": re.compile(r'^-\s*class\s+\w+', re.MULTILINE),
        "api_endpoint_change": re.compile(r'[@\']\w+\s*[=:]\s*["\'][^"\']*["\']'),
        "database_migration": re.compile(r'(DROP|ALTER|REMOVE)\s+(TABLE|COLUMN|FIELD)', re.IGNORECASE),
    }
    
    def __init__(self, diff: str, files: List[Dict]):
        self.diff = diff
        self.files = files
    
    def analyze_security(self) -> List[Dict[str, str]]:
        """Scan for security concerns."""
        concerns = []
        
        for file_info in self.files:
            filename = file_info.get("filename", "")
            patch = file_info.get("patch", "")
            
            for pattern_name, pattern in self.SECURITY_PATTERNS.items():
                matches = pattern.finditer(patch)
                for match in matches:
                    concerns.append({
                        "file": filename,
                        "type": pattern_name,
                        "line": self._get_line_number(patch, match.start()),
                        "snippet": match.group()[:100] + "..." if len(match.group()) > 100 else match.group()
                    })
        
        return concerns
    
    def analyze_breaking_changes(self) -> List[Dict[str, str]]:
        """Detect potential breaking changes."""
        breaking = []
        
        for file_info in self.files:
            filename = file_info.get("filename", "")
            patch = file_info.get("patch", "")
            
            for pattern_name, pattern in self.BREAKING_CHANGE_PATTERNS.items():
                if pattern.search(patch):
                    breaking.append({
                        "file": filename,
                        "type": pattern_name,
                        "description": f"Detected {pattern_name.replace('_', ' ')} in {filename}"
                    })
        
        return breaking
    
    def analyze_test_coverage(self) -> Dict[str, Any]:
        """Analyze test coverage changes."""
        test_files = [f for f in self.files if "test" in f.get("filename", "").lower()]
        source_files = [f for f in self.files if "test" not in f.get("filename", "").lower()]
        
        test_additions = sum(f.get("additions", 0) for f in test_files)
        test_deletions = sum(f.get("deletions", 0) for f in test_files)
        source_additions = sum(f.get("additions", 0) for f in source_files)
        
        coverage_ratio = 0
        if source_additions > 0:
            coverage_ratio = test_additions / source_additions
        
        return {
            "test_files_changed": len(test_files),
            "source_files_changed": len(source_files),
            "test_lines_added": test_additions,
            "test_lines_removed": test_deletions,
            "coverage_ratio": round(coverage_ratio, 2),
            "has_tests": len(test_files) > 0,
            "recommendation": "Add tests" if coverage_ratio < 0.5 and source_additions > 50 else "OK"
        }
    
    def generate_suggestions(self) -> List[str]:
        """Generate code improvement suggestions."""
        suggestions = []
        
        for file_info in self.files:
            filename = file_info.get("filename", "")
            patch = file_info.get("patch", "")
            additions = file_info.get("additions", 0)
            
            # Large file warning
            if additions > 500:
                suggestions.append(
                    f"⚠️ {filename}: Large addition ({additions} lines). Consider breaking into smaller PRs."
                )
            
            # TODO/FIXME detection
            todos = re.findall(r'(TODO|FIXME|XXX|HACK):?\s*(.+?)(?:\n|$)', patch, re.IGNORECASE)
            for todo_type, todo_text in todos:
                suggestions.append(
                    f"📝 {filename}: {todo_type.upper()} found - {todo_text.strip()[:80]}"
                )
            
            # Debug code detection
            if re.search(r'(console\.log|print\(|debugger|import pdb)', patch):
                suggestions.append(
                    f"🔍 {filename}: Debug code detected. Remove before merging."
                )
        
        return suggestions
    
    def _get_line_number(self, patch: str, position: int) -> int:
        """Estimate line number from patch position."""
        lines_before = patch[:position].count('\n')
        
        # Parse hunk headers to calculate actual line number
        line_number = 0
        for line in patch[:position].split('\n'):
            if line.startswith('@@'):
                match = re.search(r'\+\d+', line)
                if match:
                    line_number = int(match.group()[1:])
            elif not line.startswith('-') and not line.startswith('@@'):
                line_number += 1
        
        return max(1, line_number)


class AIAnalyzer:
    """AI-powered PR analysis using OpenAI API."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    def analyze(self, diff: str, files: List[Dict], pr_info: Dict) -> Dict[str, Any]:
        """Generate AI-powered analysis of the PR."""
        
        # Prepare context
        file_summary = "\n".join([
            f"- {f['filename']} (+{f['additions']}/-{f['deletions']})"
            for f in files[:20]  # Limit to first 20 files
        ])
        
        # Truncate diff if too long
        max_diff_length = 8000
        truncated_diff = diff[:max_diff_length]
        if len(diff) > max_diff_length:
            truncated_diff += "\n... [diff truncated due to length]"
        
        prompt = f"""Analyze this Pull Request and provide a structured review.

PR Title: {pr_info.get('title', 'N/A')}
PR Description: {pr_info.get('body', 'No description')[:500]}

Files Changed:
{file_summary}

Diff:
```diff
{truncated_diff}
```

Please provide your analysis in this JSON format:
{{
    "summary": "Brief summary of what this PR does (2-3 sentences)",
    "complexity": "Low/Medium/High",
    "risk_level": "Low/Medium/High",
    "key_changes": ["List of main changes"],
    "potential_issues": ["Any concerns or issues"],
    "recommendations": ["Suggestions for improvement"]
}}
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert code reviewer. Analyze PRs thoroughly and provide actionable feedback."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                }
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"summary": content, "error": "Could not parse JSON"}
                
        except Exception as e:
            return {"summary": f"AI analysis failed: {str(e)}", "error": str(e)}


class PRAnalyzerAgent:
    """Main agent class that orchestrates PR analysis."""
    
    def __init__(
        self, 
        github_token: str, 
        openai_key: Optional[str] = None,
        github_base_url: str = "https://api.github.com"
    ):
        self.github = GitHubAPI(github_token, github_base_url)
        self.ai = AIAnalyzer(openai_key) if openai_key else None
    
    def analyze_pr(
        self, 
        owner: str, 
        repo: str, 
        pr_number: int,
        post_comment: bool = False
    ) -> AnalysisResult:
        """Perform complete PR analysis."""
        
        # Fetch PR data
        print(f"🔍 Fetching PR #{pr_number} from {owner}/{repo}...")
        pr_info = self.github.get_pr(owner, repo, pr_number)
        diff = self.github.get_pr_diff(owner, repo, pr_number)
        files = self.github.get_pr_files(owner, repo, pr_number)
        
        # Run analysis
        print("📊 Analyzing diff patterns...")
        analyzer = DiffAnalyzer(diff, files)
        
        security_concerns = analyzer.analyze_security()
        breaking_changes = analyzer.analyze_breaking_changes()
        test_coverage = analyzer.analyze_test_coverage()
        suggestions = analyzer.generate_suggestions()
        
        # AI analysis if available
        ai_summary = "AI analysis not available"
        if self.ai:
            print("🤖 Running AI analysis...")
            ai_result = self.ai.analyze(diff, files, pr_info)
            ai_summary = ai_result.get("summary", "No summary generated")
        
        # Build result
        result = AnalysisResult(
            pr_number=pr_number,
            pr_title=pr_info.get("title", "Unknown"),
            author=pr_info.get("user", {}).get("login", "Unknown"),
            summary=ai_summary,
            files_changed=len(files),
            additions=sum(f.get("additions", 0) for f in files),
            deletions=sum(f.get("deletions", 0) for f in files),
            issues=[
                {"type": "security", "items": security_concerns},
                {"type": "breaking_changes", "items": breaking_changes}
            ],
            suggestions=suggestions,
            security_concerns=[s["description"] for s in security_concerns],
            test_coverage=test_coverage,
            breaking_changes=[b["description"] for b in breaking_changes],
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Post comment if requested
        if post_comment:
            print("💬 Posting analysis comment...")
            comment_body = self._format_comment(result)
            self.github.post_comment(owner, repo, pr_number, comment_body)
        
        return result
    
    def _format_comment(self, result: AnalysisResult) -> str:
        """Format analysis result as GitHub comment."""
        
        issues_section = ""
        if result.security_concerns:
            issues_section += "### 🚨 Security Concerns\n"
            for concern in result.security_concerns[:5]:
                issues_section += f"- {concern}\n"
            issues_section += "\n"
        
        if result.breaking_changes:
            issues_section += "### ⚠️ Breaking Changes\n"
            for change in result.breaking_changes[:5]:
                issues_section += f"- {change}\n"
            issues_section += "\n"
        
        suggestions_section = ""
        if result.suggestions:
            suggestions_section = "### 💡 Suggestions\n"
            for suggestion in result.suggestions[:5]:
                suggestions_section += f"- {suggestion}\n"
            suggestions_section += "\n"
        
        test_section = f"""### 🧪 Test Coverage
- Test files changed: {result.test_coverage['test_files_changed']}
- Coverage ratio: {result.test_coverage['coverage_ratio']}
- Status: {result.test_coverage['recommendation']}

"""
        
        return f"""## 🤖 PR Analysis Report

**Generated:** {result.timestamp}

### 📋 Summary
{result.summary}

### 📊 Statistics
| Metric | Value |
|--------|-------|
| Files Changed | {result.files_changed} |
| Lines Added | +{result.additions} |
| Lines Removed | -{result.deletions} |

{issues_section}{suggestions_section}{test_section}
---
*Generated by PR Diff Analysis Agent*
"""


def main():
    parser = argparse.ArgumentParser(
        description="PR Diff Analysis Agent - Automated code review for GitHub PRs"
    )
    parser.add_argument(
        "--owner", 
        required=True, 
        help="Repository owner (user or organization)"
    )
    parser.add_argument(
        "--repo", 
        required=True, 
        help="Repository name"
    )
    parser.add_argument(
        "--pr", 
        type=int, 
        required=True, 
        help="Pull request number"
    )
    parser.add_argument(
        "--github-token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub personal access token (or set GITHUB_TOKEN env var)"
    )
    parser.add_argument(
        "--openai-key",
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key for AI analysis (or set OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--post-comment",
        action="store_true",
        help="Post analysis as a comment on the PR"
    )
    parser.add_argument(
        "--output",
        choices=["json", "markdown", "summary"],
        default="summary",
        help="Output format"
    )
    parser.add_argument(
        "--github-base-url",
        default="https://api.github.com",
        help="GitHub API base URL (for GitHub Enterprise)"
    )
    
    args = parser.parse_args()
    
    # Validate required tokens
    if not args.github_token:
        print("❌ Error: GitHub token required. Set GITHUB_TOKEN env var or use --github-token")
        sys.exit(1)
    
    # Initialize agent
    agent = PRAnalyzerAgent(
        github_token=args.github_token,
        openai_key=args.openai_key,
        github_base_url=args.github_base_url
    )
    
    # Run analysis
    try:
        result = agent.analyze_pr(
            owner=args.owner,
            repo=args.repo,
            pr_number=args.pr,
            post_comment=args.post_comment
        )
        
        # Output results
        if args.output == "json":
            print(json.dumps(asdict(result), indent=2))
        elif args.output == "markdown":
            print(agent._format_comment(result))
        else:
            # Summary output
            print(f"\n{'='*60}")
            print(f"📊 PR Analysis Summary")
            print(f"{'='*60}")
            print(f"PR: #{result.pr_number} - {result.pr_title}")
            print(f"Author: @{result.author}")
            print(f"Files Changed: {result.files_changed}")
            print(f"Additions: +{result.additions}")
            print(f"Deletions: -{result.deletions}")
            print(f"\n📝 Summary:\n{result.summary}")
            
            if result.security_concerns:
                print(f"\n🚨 Security Concerns: {len(result.security_concerns)}")
            
            if result.breaking_changes:
                print(f"\n⚠️ Breaking Changes: {len(result.breaking_changes)}")
            
            print(f"\n💡 Suggestions: {len(result.suggestions)}")
            print(f"🧪 Test Coverage: {result.test_coverage['recommendation']}")
            
            if args.post_comment:
                print(f"\n✅ Comment posted to PR #{args.pr}")
        
        # Exit with error code if critical issues found
        if result.security_concerns or result.breaking_changes:
            sys.exit(2)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
