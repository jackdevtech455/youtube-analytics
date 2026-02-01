export function Button({
  children,
  onClick,
  variant = "default",
  disabled,
  type = "button",
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "default" | "ghost";
  disabled?: boolean;
  type?: "button" | "submit";
}) {
  const base =
    "inline-flex items-center justify-center rounded-lg px-3 py-2 text-sm font-medium transition border focus:outline-none focus:ring-2 focus:ring-yt-border";
  const styles =
    variant === "ghost"
      ? "border-yt-border bg-transparent hover:bg-yt-surface2"
      : "border-yt-border bg-yt-surface2 hover:bg-yt-surface";

  return (
    <button className={`${base} ${styles}`} onClick={onClick} disabled={disabled} type={type}>
      {children}
    </button>
  );
}
