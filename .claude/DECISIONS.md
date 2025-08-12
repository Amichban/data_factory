# Decisions Log

| Date       | Decision                                    | Why                                          | Revisit When                    |
|------------|---------------------------------------------|----------------------------------------------|---------------------------------|
| 2025-08-11 | Use FastAPI for backend API                | Python ecosystem, async support, auto-docs  | API performance < 100ms p95     |
| 2025-08-11 | Use Next.js 14 for frontend                | React Server Components, performance, DX    | Complex state management needs   |
| 2025-08-11 | Use PostgreSQL as primary database         | ACID compliance, complex queries, reliability| Data volume > 100GB             |
| 2025-08-11 | Use Redis for caching and sessions         | Performance, pub/sub capabilities            | Memory usage > 1GB              |
| 2025-08-11 | Deploy on Railway for production           | Simplicity, managed services, cost-effective | Scale beyond Railway limits     |
| 2025-08-11 | Use Docker Compose for local development   | Environment consistency, service orchestration| Local complexity increases      |
| 2025-08-11 | Implement vertical slicing approach        | End-to-end value delivery, reduced WIP       | Team grows beyond solo dev      |
| 2025-08-11 | Use Claude Code sub-agents for specialization| Focused context, role-based assistance     | Agent coordination issues       |
| 2025-08-11 | GitHub Actions for CI/CD                   | Native GitHub integration, community support | Complex deployment needs        |
| 2025-08-11 | Pre-commit hooks for code quality          | Early feedback, automated checks             | Hook execution time > 30s       |

## Architecture Principles

1. **Boring Technology**: Choose well-established, documented technologies over new/experimental ones
2. **Solo-Friendly**: Minimize operational complexity and maintenance overhead  
3. **Vertical Slices**: Each feature includes UI, API, DB, tests, and observability
4. **Feature Flags**: All new features behind flags with rollback capability
5. **Health-First**: Every service exposes /healthz and /readyz endpoints
6. **Documentation**: All decisions recorded with rationale and revisit conditions

## Decision Process

1. **Identify**: What decision needs to be made?
2. **Research**: Gather options and trade-offs
3. **Decide**: Choose option with reasoning
4. **Document**: Record in this log with date, decision, why, and revisit criteria
5. **Review**: Periodically check if revisit conditions are met

## Pending Decisions

- [ ] Authentication strategy (JWT vs Session)
- [ ] State management approach for frontend
- [ ] Monitoring and observability stack
- [ ] Testing strategy and coverage targets
- [ ] Database schema migration strategy
- [ ] Error handling and logging standards