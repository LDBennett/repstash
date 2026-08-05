"use client";

import { useState, useEffect } from "react";
import { useMutation, useQuery } from "@apollo/client/react";
import { motion } from "framer-motion";
import { PlusIcon, LinkIcon, Loader2 } from "lucide-react";
import { IMPORT_EXERCISE, GET_IMPORT_JOB } from "@/entities/exercise";
import { Button } from "@/shared/ui/button";

export function ImportExerciseForm({
  onImportSuccess,
}: {
  onImportSuccess: () => void;
}) {
  const [url, setUrl] = useState("");
  const [activeJobId, setActiveJobId] = useState<number | null>(null);

  const [importExerciseMutation, { loading: importLoading }] =
    useMutation(IMPORT_EXERCISE);

  const {
    data: jobData,
    startPolling,
    stopPolling,
  } = useQuery(GET_IMPORT_JOB, {
    variables: { id: activeJobId as number },
    skip: activeJobId === null,
  });

  useEffect(() => {
    if (jobData?.importJob) {
      const status = jobData.importJob.status;
      if (status === "COMPLETED") {
        stopPolling();
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setActiveJobId(null);
        setUrl("");
        onImportSuccess();
      } else if (status === "FAILED") {
        stopPolling();
        setActiveJobId(null);
        alert("Import failed. Please check the backend logs.");
      }
    }
  }, [jobData, stopPolling, onImportSuccess]);

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    try {
      const res = await importExerciseMutation({ variables: { url } });
      if (res.data?.importExercise?.id) {
        setActiveJobId(res.data.importExercise.id);
        startPolling(2000);
      }
    } catch (err) {
      console.error("Import error", err);
    }
  };

  const isExtracting = importLoading || activeJobId !== null;

  return (
    <motion.form
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      onSubmit={handleImport}
      className="relative max-w-3xl w-full mx-auto mb-16 z-10"
    >
      <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
        <LinkIcon className="h-6 w-6 text-text-muted" />
      </div>
      <input
        type="url"
        placeholder="Paste Instagram or TikTok URL here..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        disabled={isExtracting}
        className="w-full bg-surface-card border-2 border-surface-border rounded-full py-5 pl-16 pr-44 text-text-primary text-lg focus:outline-none focus:ring-0 focus:border-brand-amber transition-all disabled:opacity-50 shadow-2xl"
        required
      />
      <div className="absolute inset-y-2 right-2 flex items-center">
        <Button
          type="submit"
          disabled={isExtracting || !url}
          variant="primary"
          size="lg"
        >
          {isExtracting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" /> Extracting
            </>
          ) : (
            <>
              <PlusIcon className="w-5 h-5" /> Stash It
            </>
          )}
        </Button>
      </div>
    </motion.form>
  );
}
