import { useState, useMemo } from "react";
import { getDomainFromUrl } from "@/shared/lib/url";
import { ExerciseItem, ExerciseMuscle } from "./types";

export type SortConfig = {
  key: string;
  direction: "asc" | "desc";
};

export interface ExercisesData {
  myExercises: ExerciseItem[];
}

export function useFilteredExercises(exercisesData: ExercisesData | undefined) {
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: "createdAt", direction: "desc" });
  const [filterMuscle, setFilterMuscle] = useState("ALL");
  const [filterEquipment, setFilterEquipment] = useState("ALL");
  const [filterSource, setFilterSource] = useState("ALL");

  const requestSort = (key: string) => {
    let direction: "asc" | "desc" = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  const processedExercises = useMemo(() => {
    if (!exercisesData?.myExercises) return [];
    
    let result = [...exercisesData.myExercises];

    // Filters
    if (filterMuscle !== "ALL") {
      result = result.filter(ex => ex.muscles.some((m: ExerciseMuscle) => m.muscle === filterMuscle));
    }
    if (filterEquipment !== "ALL") {
      result = result.filter(ex => (ex.equipment || "BODYWEIGHT") === filterEquipment);
    }
    if (filterSource !== "ALL") {
      result = result.filter(ex => getDomainFromUrl(ex.sourceUrl).toUpperCase() === filterSource.toUpperCase());
    }

    // Sort
    result.sort((a, b) => {
      let valA, valB;
      
      if (sortConfig.key === "source") {
        valA = getDomainFromUrl(a.sourceUrl);
        valB = getDomainFromUrl(b.sourceUrl);
      } else {
        valA = (a as unknown as Record<string, unknown>)[sortConfig.key];
        valB = (b as unknown as Record<string, unknown>)[sortConfig.key];
      }
      
      if (valA == null) valA = "";
      if (valB == null) valB = "";

      if (valA < valB) {
        return sortConfig.direction === "asc" ? -1 : 1;
      }
      if (valA > valB) {
        return sortConfig.direction === "asc" ? 1 : -1;
      }
      return 0;
    });

    return result;
  }, [exercisesData, filterMuscle, filterEquipment, filterSource, sortConfig]);

  return {
    processedExercises,
    sortConfig,
    requestSort,
    filterMuscle, setFilterMuscle,
    filterEquipment, setFilterEquipment,
    filterSource, setFilterSource
  };
}
