import { gql } from "@apollo/client";

export const GET_MY_EXERCISES = gql`
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

export const IMPORT_EXERCISE = gql`
  mutation ImportExercise($url: String!) {
    importExercise(url: $url) {
      id
      status
    }
  }
`;

export const GET_IMPORT_JOB = gql`
  query GetImportJob($id: Int!) {
    importJob(id: $id) {
      id
      status
    }
  }
`;

export const GET_EXERCISE = gql`
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

export const GET_ME = gql`
  query GetMe {
    me {
      id
    }
  }
`;

export const UPDATE_EXERCISE = gql`
  mutation UpdateExercise($id: Int!, $description: String, $steps: [String!]) {
    updateExercise(id: $id, description: $description, steps: $steps) {
      id
      description
      steps
    }
  }
`;
