export function Input({
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      type={type}
      className="w-full rounded-lg border border-yt-border bg-yt-bg px-3 py-2 text-sm text-yt-text placeholder:text-yt-muted focus:outline-none focus:ring-2 focus:ring-yt-border"
    />
  );
}
