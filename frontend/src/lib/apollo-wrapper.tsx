"use client";

import {
  ApolloLink,
  HttpLink,
} from "@apollo/client";
import { setContext } from "@apollo/client/link/context";
import { useAuth } from "@clerk/nextjs";
import {
  ApolloNextAppProvider,
  ApolloClient,
  InMemoryCache,
  SSRMultipartLink,
} from "@apollo/client-integration-nextjs";

export function ApolloWrapper({ children }: React.PropsWithChildren) {
  const { getToken } = useAuth();

  const makeClient = () => {
    const httpLink = new HttpLink({
        uri: "http://localhost:8000/graphql", // FastAPI endpoint
        fetchOptions: { cache: "no-store" }, // Opt out of Next.js caching for mutations
    });

    const authLink = setContext(async (_, { headers }) => {
      const token = await getToken();
      return {
        headers: {
          ...headers,
          authorization: token ? `Bearer ${token}` : "",
        }
      }
    });

    return new ApolloClient({
      cache: new InMemoryCache(),
      link:
        typeof window === "undefined"
          ? ApolloLink.from([
              new SSRMultipartLink({
                stripDefer: true,
              }),
              authLink,
              httpLink,
            ])
          : ApolloLink.from([authLink, httpLink]),
    });
  };

  return (
    <ApolloNextAppProvider makeClient={makeClient}>
      {children}
    </ApolloNextAppProvider>
  );
}
