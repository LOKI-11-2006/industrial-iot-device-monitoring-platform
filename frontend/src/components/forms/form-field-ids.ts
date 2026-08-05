export function fieldDescriptionIds(inputId: string, hasHint: boolean, hasError: boolean) {
  return [hasHint ? `${inputId}-hint` : null, hasError ? `${inputId}-error` : null]
    .filter(Boolean)
    .join(" ") || undefined;
}
