interface AtidepLogoProps {
  className?: string;
  size?: number;
}

export const AtidepLogo = ({ className = "w-8 h-8", size = 32 }: AtidepLogoProps) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 36 36"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <path
      d="M18 2.5L31 7.2C31 16.5 25.5 26.2 18 33.5C10.5 26.2 5 16.5 5 7.2L18 2.5Z"
      fill="currentColor"
      opacity="0.15"
    />
    <path
      d="M18 3.5L30 7.8C30 16.2 24.8 25.2 18 32C11.2 25.2 6 16.2 6 7.8L18 3.5Z"
      stroke="currentColor"
      strokeWidth="1.3"
      fill="none"
      opacity="0.5"
    />
    <path
      d="M18 8.5L10.5 24.5H13.8L15.6 20.2H20.4L22.2 24.5H25.5L18 8.5Z M18 13.2L16.4 17.5H19.6L18 13.2Z"
      fill="currentColor"
      fillRule="evenodd"
    />
  </svg>
);
