"use client";

import { gql } from "@apollo/client";
import { useQuery } from "@apollo/client/react";
import { UserButton } from "@clerk/nextjs";

const GET_ME = gql`
  query GetMe {
    me {
      id
      email
      unitPreference
    }
  }
`;

export default function Dashboard() {
  const { data, loading, error } = useQuery(GET_ME);

  return (
    <div className="min-h-screen bg-surface-background p-10 flex flex-col items-center">
      <div className="w-full max-w-2xl bg-surface-card border border-surface-border rounded-xl p-8 text-center text-text-primary mt-10">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <UserButton afterSignOutUrl="/" />
        </div>
        
        {loading && <p className="text-brand-amber">Verifying token with backend...</p>}
        {error && <p className="text-red-400 text-left p-4 bg-red-500/10 rounded">Auth Error: {error.message}</p>}
        {data && (
          <div className="bg-brand-muted/20 p-6 rounded-lg text-left mt-4 border border-brand-amber/10">
            <h2 className="text-xl font-semibold mb-2 text-brand-amber">✅ Auth Successful!</h2>
            <p className="text-text-muted">The backend verified your Clerk token and returned your DB user record:</p>
            <pre className="mt-4 p-4 bg-surface-background rounded text-sm text-text-primary overflow-x-auto border border-surface-border">
              {JSON.stringify(data.me, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
