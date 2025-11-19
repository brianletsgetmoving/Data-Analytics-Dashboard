interface SkeletonLoaderProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  variant?: 'card' | 'text' | 'circle';
}

function SkeletonLoader({ 
  width = '100%', 
  height = '100%', 
  className = '',
  variant = 'card'
}: SkeletonLoaderProps) {
  const baseClasses = 'neo-skeleton';
  const variantClasses = {
    card: 'neo-rounded',
    text: 'h-4',
    circle: 'rounded-full',
  };

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={{ width, height }}
      aria-label="Loading..."
      role="status"
    />
  );
}

export default SkeletonLoader;

