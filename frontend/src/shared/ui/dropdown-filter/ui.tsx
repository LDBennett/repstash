"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

export function DropdownFilter({ 
  label, 
  options, 
  value, 
  onChange 
}: { 
  label: string; 
  options: string[]; 
  value: string; 
  onChange: (val: string) => void;
}) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      {isOpen && (
        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
      )}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="relative z-50 flex items-center justify-between gap-3 px-4 py-2.5 bg-surface-card border border-surface-border rounded-xl text-sm font-semibold hover:border-brand-amber/50 transition-colors shadow-sm"
      >
        <div className="flex items-center gap-1.5">
          <span className="text-text-muted">{label}:</span>
          <span className="text-brand-amber">{value.replace("_", " ")}</span>
        </div>
        <ChevronDown className={`w-4 h-4 text-text-muted transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="absolute left-0 top-full mt-2 z-50 w-72 bg-surface-card border border-surface-border rounded-2xl shadow-2xl p-3 origin-top-left"
          >
            <div className="grid grid-cols-2 gap-2">
              {options.map(opt => (
                <button
                  key={opt}
                  onClick={() => {
                    onChange(opt);
                    setIsOpen(false);
                  }}
                  className={`px-3 py-2.5 rounded-xl text-xs font-semibold transition-colors text-left flex items-center ${
                    value === opt 
                      ? 'bg-brand-amber text-white shadow-md shadow-brand-amber/20' 
                      : 'hover:bg-surface-background text-text-primary'
                  }`}
                >
                  {opt.replace("_", " ")}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
