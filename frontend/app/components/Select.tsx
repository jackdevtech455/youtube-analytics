"use client";

export type SelectOption<TValue extends string> = {
  value: TValue;
  label: string;
};

export function Select<TValue extends string>({
  value,
  onChange,
  options,
}: {
  value: TValue;
  onChange: (value: TValue) => void;
  options: ReadonlyArray<SelectOption<TValue>>;
}) {
  return (
    <select
      className="w-full rounded-lg border border-yt-border bg-yt-surface2 px-3 py-2 text-sm text-yt-text outline-none focus:ring-2 focus:ring-yt-border"
      value={value}
      onChange={(event) => onChange(event.target.value as TValue)}
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
