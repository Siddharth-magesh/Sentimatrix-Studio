import Link from 'next/link';
import { ArrowRight, BarChart3, Zap, Shield } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-white">
      {/* Header */}
      <header className="border-b border-neutral-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-semibold">Sentimatrix Studio</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link
              href="/auth/login"
              className="text-sm font-medium text-neutral-600 hover:text-neutral-900"
            >
              Sign in
            </Link>
            <Link
              href="/auth/register"
              className="btn-primary btn-sm"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="py-20 text-center sm:py-32">
          <h1 className="text-4xl font-bold tracking-tight text-neutral-900 sm:text-6xl">
            Sentiment Analysis
            <br />
            <span className="text-primary-600">Without Code</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-neutral-600">
            Analyze social media sentiment, reviews, and feedback with powerful AI.
            No coding required. Get actionable insights in minutes.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link href="/auth/register" className="btn-primary btn-lg">
              Start Free Trial
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link href="#features" className="btn-outline btn-lg">
              Learn More
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <section id="features" className="py-20">
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              icon={<Zap className="h-6 w-6" />}
              title="Lightning Fast"
              description="Analyze thousands of data points in seconds with our optimized pipeline."
            />
            <FeatureCard
              icon={<BarChart3 className="h-6 w-6" />}
              title="Deep Insights"
              description="Get sentiment, emotions, and key themes from your data automatically."
            />
            <FeatureCard
              icon={<Shield className="h-6 w-6" />}
              title="Secure & Private"
              description="Your data is encrypted and never shared. GDPR compliant."
            />
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-200 py-8">
        <div className="mx-auto max-w-7xl px-4 text-center text-sm text-neutral-500 sm:px-6 lg:px-8">
          Powered by Sentimatrix
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="card p-6">
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
        {icon}
      </div>
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      <p className="text-neutral-600">{description}</p>
    </div>
  );
}
