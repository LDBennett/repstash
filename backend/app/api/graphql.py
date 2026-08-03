import strawberry
from app.domains.imports.graphql import ImportMutation, ImportQuery
from app.domains.exercises.graphql import ExerciseQuery, ExerciseMutation

from app.domains.users.graphql import UserType

@strawberry.type
class Query(ExerciseQuery, ImportQuery):

    @strawberry.field
    def me(self, info: strawberry.Info) -> UserType:
        user = info.context.get("user")
        if not user:
            raise Exception("Unauthorized: You must be logged in")
        return user

@strawberry.type
class Mutation(ImportMutation, ExerciseMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
