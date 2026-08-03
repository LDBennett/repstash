import strawberry
from app.domains.imports.graphql import ImportMutation

from app.domains.users.graphql import UserType

@strawberry.type
class Query:

    @strawberry.field
    def me(self, info: strawberry.Info) -> UserType:
        user = info.context.get("user")
        if not user:
            raise Exception("Unauthorized: You must be logged in")
        return user

@strawberry.type
class Mutation(ImportMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
