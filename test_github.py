from services.github_service import GitHubService
service = GitHubService()
try:
    rl = service.g.get_rate_limit().rate
    print(f"Limit: {rl.limit}, Remaining: {rl.remaining}")
except Exception as e:
    print(f"Error: {e}")
