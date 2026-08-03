import strawberry
from app.domains.imports.graphql import ImportMutation
from app.domains.exercises.graphql import ExerciseType
from typing import List

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Welcome to RepStash GraphQL API"

@strawberry.type
class Mutation(ImportMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
