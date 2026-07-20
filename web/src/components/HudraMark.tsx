/** Cross mark from the Hudra brand — inherits text color via currentColor. */
export function HudraMark({
  className,
  title = "Hudra",
}: {
  className?: string;
  title?: string;
}) {
  return (
    <svg
      className={className}
      width="48"
      height="64"
      viewBox="0 0 48 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label={title}
    >
      <title>{title}</title>
      <path
        d="M32 8C32 10.2091 30.2091 12 28 12V20H36C36 17.7909 37.7909 16 40 16C42.2091 16 44 17.7909 44 20C46.2091 20 48 21.7909 48 24C48 26.2091 46.2091 28 44 28C44 30.2091 42.2091 32 40 32C37.7909 32 36 30.2091 36 28H28V45H32V51H38V57H44V64H4V57H10V51H16V45H20V28H12C12 30.2091 10.2091 32 8 32C5.79086 32 4 30.2091 4 28C1.79086 28 0 26.2091 0 24C0 21.7909 1.79086 20 4 20C4 17.7909 5.79086 16 8 16C10.2091 16 12 17.7909 12 20H20V12C17.7909 12 16 10.2091 16 8C16 5.79086 17.7909 4 20 4C20 1.79086 21.7909 0 24 0C26.2091 0 28 1.79086 28 4C30.2091 4 32 5.79086 32 8Z"
        fill="currentColor"
      />
    </svg>
  );
}
