import { X, PlusIcon } from "lucide-react";
import { Button } from "@/shared/ui/button";

export function ExerciseSteps({
  isEditing,
  steps,
  editSteps,
  onStepChange,
  onAddStep,
  onRemoveStep,
}: {
  isEditing: boolean;
  steps: string[];
  editSteps: string[];
  onStepChange: (index: number, val: string) => void;
  onAddStep: () => void;
  onRemoveStep: (index: number) => void;
}) {
  if (isEditing) {
    return (
      <div className="space-y-3">
        {editSteps.map((step, idx) => (
          <div key={idx} className="flex items-start gap-3">
            <div className="shrink-0 w-8 h-8 rounded-full bg-brand-amber/20 text-brand-amber flex items-center justify-center font-bold text-sm mt-1">
              {idx + 1}
            </div>
            <textarea
              value={step}
              onChange={(e) => onStepChange(idx, e.target.value)}
              rows={2}
              className="flex-1 bg-surface-background border border-brand-amber/30 rounded-xl p-3 text-text-primary text-sm focus:outline-none focus:border-brand-amber focus-visible:ring-1 focus-visible:ring-brand-amber"
            />
            <Button
              onClick={() => window.confirm("Are you sure you want to delete this step?") && onRemoveStep(idx)}
              variant="icon"
              size="icon"
              className="mt-1 hover:text-red-400 p-3"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        ))}
        <Button
          onClick={onAddStep}
          variant="ghost"
          size="none"
          className="mt-4 text-sm"
        >
          <PlusIcon className="w-4 h-4" /> Add Step
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {steps?.length > 0 ? (
        steps.map((step: string, idx: number) => (
          <div key={idx} className="flex gap-4">
            <div className="shrink-0 w-8 h-8 rounded-full bg-surface-border text-text-muted flex items-center justify-center font-bold text-sm">
              {idx + 1}
            </div>
            <p className="text-text-primary leading-relaxed mt-1">{step}</p>
          </div>
        ))
      ) : (
        <p className="text-text-muted italic">
          No step-by-step instructions available.
        </p>
      )}
    </div>
  );
}
