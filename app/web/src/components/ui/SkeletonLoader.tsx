interface SkeletonLoaderProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  variant?: 'card' | 'text' | 'circle' | 'chart';
}

function SkeletonLoader({ 
  width = '100%', 
  height = '100%', 
  className = '',
  variant = 'card'
}: SkeletonLoaderProps) {
  const baseClasses = 'animate-pulse bg-gray-200 dark:bg-slate-700';
  const variantClasses = {
    card: 'rounded-xl',
    text: 'h-4 rounded',
    circle: 'rounded-full',
    chart: 'rounded-xl',
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

