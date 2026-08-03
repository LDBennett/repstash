"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@apollo/client/react";
import { motion } from "framer-motion";
import { Link as LinkIcon, Loader2, Edit2, Check, X, ShieldAlert } from "lucide-react";
import { GET_EXERCISE, GET_ME, UPDATE_EXERCISE } from "@/entities/exercise";
import { useRouter } from "next/navigation";

export function ExerciseDetailWidget({ id }: { id: number }) {
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [editDesc, setEditDesc] = useState("");
  const [editSteps, setEditSteps] = useState<string[]>([]);

  const { data: exerciseData, loading: exerciseLoading, error: exerciseError } = useQuery(GET_EXERCISE, {
    variables: { id },
  });

  const { data: meData } = useQuery(GET_ME, { errorPolicy: "ignore" });

  const [updateExercise, { loading: updating }] = useMutation(UPDATE_EXERCISE);

  const exercise = exerciseData?.exercise;
  const isOwner = meData?.me?.id === exercise?.userId;

  useEffect(() => {
    if (isEditing && exercise) {
      setEditDesc(exercise.description || "");
      setEditSteps([...(exercise.steps || [])]);
    }
  }, [isEditing, exercise]);

  const handleSave = async () => {
    try {
      await updateExercise({
        variables: {
          id,
          description: editDesc,
          steps: editSteps.filter(s => s.trim().length > 0)
        }
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
        <h1 className="text-2xl font-bold text-text-primary mb-2">Exercise Not Found</h1>
        <p className="text-text-muted mb-8">This exercise may have been deleted or does not exist.</p>
        <button onClick={() => router.push('/dashboard')} className="px-6 py-3 bg-brand-amber rounded-full text-white font-bold hover:bg-brand-hover">
          Back to Dashboard
        </button>
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
          {isOwner && !isEditing && (
            <button 
              onClick={() => setIsEditing(true)}
              className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-full border border-surface-border bg-surface-background text-text-primary hover:border-brand-amber hover:text-brand-amber transition-colors font-semibold"
            >
              <Edit2 className="w-4 h-4" /> Edit
            </button>
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
            <h2 className="text-xl font-bold text-text-primary mb-6">Instructions</h2>
            {isEditing ? (
              <div className="space-y-3">
                {editSteps.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-brand-amber/20 text-brand-amber flex items-center justify-center font-bold text-sm mt-1">
                      {idx + 1}
                    </div>
                    <textarea 
                      value={step}
                      onChange={(e) => handleStepChange(idx, e.target.value)}
                      rows={2}
                      className="flex-1 bg-surface-background border border-brand-amber/30 rounded-xl p-3 text-text-primary text-sm focus:outline-none focus:border-brand-amber"
                    />
                    <button onClick={() => removeStep(idx)} className="p-2 text-text-muted hover:text-red-400 mt-1">
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                ))}
                <button onClick={addStep} className="text-brand-amber text-sm font-bold flex items-center gap-1 mt-4 hover:underline">
                  <Plus className="w-4 h-4" /> Add Step
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {exercise.steps?.length > 0 ? (
                  exercise.steps.map((step: string, idx: number) => (
                    <div key={idx} className="flex gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-surface-border text-text-muted flex items-center justify-center font-bold text-sm">
                        {idx + 1}
                      </div>
                      <p className="text-text-primary leading-relaxed mt-1">{step}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-text-muted italic">No step-by-step instructions available.</p>
                )}
              </div>
            )}
          </section>
        </div>

        {/* Sidebar Area */}
        <div className="space-y-8">
          <div className="bg-surface-background border border-surface-border rounded-2xl p-6">
            <h3 className="text-sm font-bold text-text-muted uppercase tracking-wider mb-4">Target Muscles</h3>
            <div className="flex flex-wrap gap-2">
              {exercise.muscles?.length > 0 ? (
                exercise.muscles.map((m: any, i: number) => (
                  <span key={i} className="px-3 py-1.5 bg-brand-amber/10 border border-brand-amber/20 text-brand-amber text-sm font-semibold rounded-lg">
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
              <button 
                onClick={handleSave}
                disabled={updating}
                className="w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30 transition-colors font-bold"
              >
                {updating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />} Save Changes
              </button>
              <button 
                onClick={() => setIsEditing(false)}
                disabled={updating}
                className="w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-surface-border text-text-primary hover:bg-surface-border/80 transition-colors font-bold"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
