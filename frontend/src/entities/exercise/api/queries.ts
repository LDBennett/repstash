import { gql, TypedDocumentNode } from "@apollo/client";
import { ExerciseDetail, ExerciseItem } from "../model/types";

export const GET_MY_EXERCISES: TypedDocumentNode<{
  myExercises: ExerciseItem[];
}> = gql`
  query GetMyExercises {
    myExercises {
      id
      title
      description
      category
      equipment
      sourceUrl
      createdAt
      muscles {
        muscle
        role
      }
    }
  }
`;

export const IMPORT_EXERCISE: TypedDocumentNode<
  { importExercise: { id: number; status: string } },
  { url: string }
> = gql`
  mutation ImportExercise($url: String!) {
    importExercise(url: $url) {
      id
      status
    }
  }
`;

export const GET_IMPORT_JOB: TypedDocumentNode<
  { importJob: { id: number; status: string } },
  { id: number }
> = gql`
  query GetImportJob($id: Int!) {
    importJob(id: $id) {
      id
      status
    }
  }
`;

export const GET_EXERCISE: TypedDocumentNode<
  { exercise: ExerciseDetail },
  { id: number }
> = gql`
  query GetExercise($id: Int!) {
    exercise(id: $id) {
      id
      userId
      title
      description
      category
      equipment
      sourceUrl
      steps
      muscles {
        muscle
        role
      }
    }
  }
`;

export const GET_ME: TypedDocumentNode<{ me: { id: number } | null }> = gql`
  query GetMe {
    me {
      id
    }
  }
`;

export const UPDATE_EXERCISE: TypedDocumentNode<
  { updateExercise: { id: number; description: string; steps: string[] } },
  { id: number; description?: string; steps?: string[] }
> = gql`
  mutation UpdateExercise($id: Int!, $description: String, $steps: [String!]) {
    updateExercise(id: $id, description: $description, steps: $steps) {
      id
      description
      steps
    }
  }
`;
