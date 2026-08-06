export interface ExerciseMuscle {
  muscle: string;
  role: string;
}

export interface ExerciseItem {
  id: number;
  title: string;
  description: string | null;
  category: string | null;
  equipment: string | null;
  sourceUrl: string;
  thumbnailUrl: string | null;
  createdAt: string;
  muscles: ExerciseMuscle[];
}

export interface ExerciseDetail extends ExerciseItem {
  userId: number;
  steps: string[];
}
