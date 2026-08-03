"use client";

import { useQuery } from "@apollo/client/react";
import { motion } from "framer-motion";
import { Loader2, Play, Filter, ArrowUpDown, Link as LinkIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { GET_MY_EXERCISES } from "@/entities/exercise";
import { useFilteredExercises } from "@/entities/exercise";
import { DropdownFilter } from "@/shared/ui/dropdown-filter";
import { getDomainFromUrl } from "@/shared/lib/url";
import { ImportExerciseForm } from "@/features/import-exercise";

const MUSCLE_OPTIONS = ["ALL", "QUADRICEPS", "HAMSTRINGS", "GLUTES", "CHEST", "LATS", "UPPER_BACK", "BICEPS", "TRICEPS", "ABS"];
const EQUIPMENT_OPTIONS = ["ALL", "BARBELL", "DUMBBELL", "KETTLEBELL", "CABLE", "MACHINE", "SMITH_MACHINE", "BODYWEIGHT", "RESISTANCE_BAND", "OTHER"];
const SOURCE_OPTIONS = ["ALL", "INSTAGRAM", "TIKTOK", "YOUTUBE"];

export function DashboardStashWidget() {
  const router = useRouter();
  
  const { data: exercisesData, loading: exercisesLoading, refetch: refetchExercises } = useQuery(GET_MY_EXERCISES);

  const {
    processedExercises,
    sortConfig,
    requestSort,
    filterMuscle, setFilterMuscle,
    filterEquipment, setFilterEquipment,
    filterSource, setFilterSource
  } = useFilteredExercises(exercisesData);

  return (
    <>
      {/* Import Feature Layer */}
      <ImportExerciseForm onImportSuccess={refetchExercises} />

      {/* Widget UI Layer */}
      <div className="w-full max-w-7xl mx-auto z-10 relative flex-1 flex flex-col pb-20">
        <h2 className="text-2xl font-bold text-text-primary mb-6 flex items-center gap-3">
          Your Stash
        </h2>

        {exercisesLoading ? (
          <div className="flex-1 flex justify-center items-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-brand-amber" />
          </div>
        ) : exercisesData?.myExercises?.length === 0 && filterMuscle === "ALL" && filterEquipment === "ALL" && filterSource === "ALL" ? (
          <div className="flex-1 flex flex-col items-center justify-center py-20 border-2 border-dashed border-surface-border rounded-3xl bg-surface-card/30">
            <div className="bg-surface-border/50 p-4 rounded-full mb-4">
              <Play className="w-10 h-10 text-text-muted pl-1" />
            </div>
            <h3 className="text-xl font-medium text-text-primary mb-2">Your stash is empty</h3>
            <p className="text-text-muted max-w-sm text-center">Paste a video link above to instantly extract your first exercise using AI.</p>
          </div>
        ) : (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-surface-card border border-surface-border rounded-3xl overflow-hidden shadow-2xl flex flex-col"
          >
            {/* Custom Filter Popovers */}
            <div className="p-6 border-b border-surface-border bg-surface-background/30 flex flex-wrap gap-4 items-center">
              <div className="flex items-center gap-2 text-text-muted mr-2">
                <Filter className="w-4 h-4" />
                <span className="text-sm font-semibold uppercase tracking-wider">Filters</span>
              </div>
              
              <DropdownFilter 
                label="Muscle" 
                options={MUSCLE_OPTIONS} 
                value={filterMuscle} 
                onChange={setFilterMuscle} 
              />
              
              <DropdownFilter 
                label="Equipment" 
                options={EQUIPMENT_OPTIONS} 
                value={filterEquipment} 
                onChange={setFilterEquipment} 
              />
              
              <DropdownFilter 
                label="Source" 
                options={SOURCE_OPTIONS} 
                value={filterSource} 
                onChange={setFilterSource} 
              />
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-text-primary">
                <thead className="text-xs text-text-muted uppercase bg-surface-background/50 border-b border-surface-border">
                  <tr>
                    <th scope="col" className="px-6 py-4 cursor-pointer hover:text-brand-amber transition-colors select-none" onClick={() => requestSort('title')}>
                      <div className="flex items-center gap-2">Exercise {sortConfig.key === 'title' && <ArrowUpDown className="w-3 h-3 text-brand-amber"/>}</div>
                    </th>
                    <th scope="col" className="px-6 py-4 cursor-pointer hover:text-brand-amber transition-colors select-none" onClick={() => requestSort('equipment')}>
                      <div className="flex items-center gap-2">Equipment {sortConfig.key === 'equipment' && <ArrowUpDown className="w-3 h-3 text-brand-amber"/>}</div>
                    </th>
                    <th scope="col" className="px-6 py-4 cursor-pointer hover:text-brand-amber transition-colors select-none" onClick={() => requestSort('source')}>
                      <div className="flex items-center gap-2">Source {sortConfig.key === 'source' && <ArrowUpDown className="w-3 h-3 text-brand-amber"/>}</div>
                    </th>
                    <th scope="col" className="px-6 py-4 cursor-pointer hover:text-brand-amber transition-colors select-none" onClick={() => requestSort('createdAt')}>
                      <div className="flex items-center gap-2">Date Added {sortConfig.key === 'createdAt' && <ArrowUpDown className="w-3 h-3 text-brand-amber"/>}</div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {processedExercises.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-6 py-12 text-center text-text-muted">
                        No exercises match your current filters.
                      </td>
                    </tr>
                  ) : (
                    processedExercises.map((ex: any) => (
                      <tr 
                        key={ex.id} 
                        onClick={() => router.push(`/exercises/${ex.id}`)}
                        className="bg-surface-card border-b border-surface-border hover:bg-surface-background/70 transition-colors last:border-0 cursor-pointer group"
                      >
                        <td className="px-6 py-5">
                           <div className="font-bold text-base mb-1.5 group-hover:text-brand-amber transition-colors">{ex.title}</div>
                           <div className="flex flex-wrap gap-1.5">
                             {ex.muscles?.map((m: any, i: number) => (
                                <span key={i} className="text-[10px] font-semibold text-brand-amber bg-brand-amber/10 px-2 py-0.5 rounded uppercase tracking-wider">
                                  {m.muscle}
                                </span>
                             ))}
                           </div>
                        </td>
                        <td className="px-6 py-5">
                          <span className="bg-surface-background border border-surface-border px-3 py-1.5 rounded-lg text-xs font-semibold text-text-primary">
                            {ex.equipment?.replace("_", " ") || "BODYWEIGHT"}
                          </span>
                        </td>
                        <td className="px-6 py-5">
                          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${
                            getDomainFromUrl(ex.sourceUrl) === 'Instagram' ? 'bg-pink-500/10 text-pink-400 border border-pink-500/20' :
                            getDomainFromUrl(ex.sourceUrl) === 'TikTok' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' :
                            getDomainFromUrl(ex.sourceUrl) === 'YouTube' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                            'bg-surface-background text-text-primary border border-surface-border'
                          }`}>
                            {getDomainFromUrl(ex.sourceUrl) === 'TikTok' && (
                              <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M19.589 6.686a4.793 4.793 0 0 1-3.77-4.245V2h-3.445v13.672a2.896 2.896 0 0 1-5.201 1.743l-.002-.001.002.001a2.895 2.895 0 0 1 3.183-4.51v-3.5a6.329 6.329 0 0 0-5.394 10.692 6.33 6.33 0 0 0 10.857-4.424V8.687a8.182 8.182 0 0 0 4.773 1.526V6.79a4.831 4.831 0 0 1-1.003-.104z"/></svg>
                            )}
                            {getDomainFromUrl(ex.sourceUrl) === 'Instagram' && (
                              <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>
                            )}
                            {getDomainFromUrl(ex.sourceUrl) === 'YouTube' && (
                              <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
                            )}
                            {getDomainFromUrl(ex.sourceUrl) === 'Other' && <LinkIcon className="w-3.5 h-3.5" />}
                            {getDomainFromUrl(ex.sourceUrl)}
                          </span>
                        </td>
                        <td className="px-6 py-5 text-text-muted">
                          {new Date(ex.createdAt).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </div>
    </>
  );
}
