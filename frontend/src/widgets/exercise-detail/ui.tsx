"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@apollo/client/react";
import { motion } from "framer-motion";
import {
  Link as LinkIcon,
  Loader2,
  Edit2,
  Check,
  X,
  ShieldAlert,
  PlusIcon,
} from "lucide-react";
import { GET_EXERCISE, GET_ME, UPDATE_EXERCISE } from "@/entities/exercise";
import { useRouter } from "next/navigation";
import { Button } from "@/shared/ui/button";
import { ExerciseSteps } from "./exercise-steps";

export function ExerciseDetailWidget({ id }: { id: number }) {
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [editDesc, setEditDesc] = useState("");
  const [editSteps, setEditSteps] = useState<string[]>([]);

  const {
    data: exerciseData,
    loading: exerciseLoading,
    error: exerciseError,
  } = useQuery(GET_EXERCISE, {
    variables: { id },
  });

  const { data: meData } = useQuery(GET_ME, { errorPolicy: "ignore" });

  const [updateExercise, { loading: updating }] = useMutation(UPDATE_EXERCISE);

  const exercise = exerciseData?.exercise;
  const isOwner = meData?.me?.id === exercise?.userId;

  const handleSave = async () => {
    try {
      await updateExercise({
        variables: {
          id,
          description: editDesc,
          steps: editSteps.filter((s) => s.trim().length > 0),
        },
      });
      setIsEditing(false);
    } catch (err) {
      console.error("Failed to update", err);
      alert("Failed to save changes.");
    }
  };

  const handleStepChange = (index: number, val: string) => {
    const newSteps = [...editSteps];
    newSteps[index] = val;
    setEditSteps(newSteps);
  };

  const addStep = () => {
    setEditSteps([...editSteps, ""]);
  };

  const removeStep = (index: number) => {
    setEditSteps(editSteps.filter((_, i) => i !== index));
  };

  if (exerciseLoading) {
    return (
      <div className="flex-1 flex items-center justify-center py-32">
        <Loader2 className="w-12 h-12 animate-spin text-brand-amber" />
      </div>
    );
  }

  if (exerciseError || !exercise) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center py-32">
        <ShieldAlert className="w-16 h-16 text-red-500 mb-4" />
        <h1 className="text-2xl font-bold text-text-primary mb-2">
          Exercise Not Found
        </h1>
        <p className="text-text-muted mb-8">
          This exercise may have been deleted or does not exist.
        </p>
        <Button
          onClick={() => router.push("/dashboard")}
          variant="primary"
          size="lg"
        >
          Back to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto bg-surface-card border border-surface-border rounded-3xl p-8 md:p-12 shadow-2xl relative z-10"
    >
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8 border-b border-surface-border pb-8">
        <div>
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="text-xs font-bold px-3 py-1 bg-surface-background border border-surface-border rounded-full text-text-muted uppercase tracking-wider">
              {exercise.category || "General"}
            </span>
            <span className="text-xs font-bold px-3 py-1 bg-surface-background border border-surface-border rounded-full text-brand-amber uppercase tracking-wider">
              {exercise.equipment?.replace("_", " ") || "Bodyweight"}
            </span>
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold text-text-primary tracking-tight leading-tight">
            {exercise.title}
          </h1>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {!isEditing && isOwner && (
            <Button
              onClick={() => {
                setIsEditing(true);
                setEditDesc(exercise.description || "");
                setEditSteps([...(exercise.steps || [])]);
              }}
              variant="outline"
              size="md"
            >
              <Edit2 className="w-4 h-4" /> Edit
            </Button>
          )}
          {exercise.sourceUrl && (
            <a
              href={exercise.sourceUrl}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-full bg-brand-amber text-white font-semibold hover:bg-brand-hover transition-colors shadow-lg shadow-brand-amber/20"
            >
              <LinkIcon className="w-4 h-4" /> Watch Video
            </a>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
        {/* Main Content Area */}
        <div className="md:col-span-2 space-y-10">
          <section>
            <h2 className="text-xl font-bold text-text-primary mb-4 flex items-center gap-2">
              Overview
            </h2>
            {isEditing ? (
              <textarea
                value={editDesc}
                onChange={(e) => setEditDesc(e.target.value)}
                rows={4}
                className="w-full bg-surface-background border border-brand-amber/50 rounded-xl p-4 text-text-primary focus:outline-none focus:ring-1 focus:ring-brand-amber"
                placeholder="Enter a description..."
              />
            ) : (
              <p className="text-text-muted leading-relaxed text-lg">
                {exercise.description || "No description provided."}
              </p>
            )}
          </section>

          <section>
            <h2 className="text-xl font-bold text-text-primary mb-6">
              Instructions
            </h2>
            <ExerciseSteps
              isEditing={isEditing}
              steps={exercise.steps || []}
              editSteps={editSteps}
              onStepChange={handleStepChange}
              onAddStep={addStep}
              onRemoveStep={removeStep}
            />
          </section>
        </div>

        {/* Sidebar Area */}
        <div className="space-y-8">
          <div className="bg-surface-background border border-surface-border rounded-2xl p-6">
            <h3 className="text-sm font-bold text-text-muted uppercase tracking-wider mb-4">
              Target Muscles
            </h3>
            <div className="flex flex-wrap gap-2">
              {exercise.muscles?.length > 0 ? (
                exercise.muscles.map((m: { muscle: string }, i: number) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 bg-brand-amber/10 border border-brand-amber/20 text-brand-amber text-sm font-semibold rounded-lg"
                  >
                    {m.muscle.replace("_", " ")}
                  </span>
                ))
              ) : (
                <span className="text-text-muted text-sm">Not specified</span>
              )}
            </div>
          </div>

          {isEditing && (
            <div className="bg-surface-background border border-surface-border rounded-2xl p-6 flex flex-col gap-3">
              <Button
                onClick={handleSave}
                disabled={updating}
                variant="success"
                size="md"
                fullWidth
              >
                {updating ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Check className="w-5 h-5" />
                )}{" "}
                Save Changes
              </Button>
              <Button
                onClick={() => setIsEditing(false)}
                disabled={updating}
                variant="secondary"
                size="md"
                fullWidth
              >
                Cancel
              </Button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
