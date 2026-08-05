import { ButtonHTMLAttributes, forwardRef, ReactNode } from "react";

export type ButtonVariant = 
  | "primary"
  | "secondary"
  | "outline"
  | "ghost"
  | "icon"
  | "success"
  | "danger";

export type ButtonSize = "sm" | "md" | "lg" | "xl" | "icon" | "none";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children?: ReactNode;
  fullWidth?: boolean;
  className?: string;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: "bg-brand-amber text-white font-semibold hover:bg-brand-hover shadow-lg shadow-brand-amber/20",
  secondary: "bg-surface-border text-text-primary hover:bg-surface-border/80 font-bold",
  outline: "border border-surface-border bg-surface-background text-text-primary hover:border-brand-amber hover:text-brand-amber font-semibold",
  ghost: "text-brand-amber font-bold hover:underline",
  icon: "text-text-muted hover:text-red-400",
  success: "bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30 font-bold",
  danger: "bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 font-bold",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "px-4 py-2 text-sm rounded-full",
  md: "px-5 py-2.5 rounded-full",
  lg: "px-6 py-3 rounded-full",
  xl: "px-8 py-4 text-lg rounded-full",
  icon: "p-2 rounded-lg",
  none: "",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      fullWidth = false,
      className = "",
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    // Determine if we need to apply flex center
    const isIconVariant = variant === "icon";
    const baseStyle = isIconVariant
      ? "inline-flex items-center justify-center transition-colors focus:outline-none"
      : "inline-flex items-center justify-center gap-2 transition-colors focus:outline-none";

    const widthStyle = fullWidth ? "w-full rounded-xl" : "";
    const disabledStyle = disabled ? "opacity-50 cursor-not-allowed" : "";

    const combinedClassName = [
      baseStyle,
      variantStyles[variant],
      sizeStyles[size],
      widthStyle,
      disabledStyle,
      className,
    ]
      .filter(Boolean)
      .join(" ");

    return (
      <button
        ref={ref}
        className={combinedClassName}
        disabled={disabled}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
