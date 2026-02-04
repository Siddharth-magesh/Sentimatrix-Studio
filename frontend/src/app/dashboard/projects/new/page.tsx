'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Input,
  Label,
  Textarea,
  Select,
  Checkbox,
  Alert,
} from '@/components/ui';
import { PlatformLinksInput, PLATFORMS } from '@/components/forms';
import { useCreateProject, usePresets, useLLMProviders } from '@/hooks';
import type { PlatformLinks, ProductInfo } from '@/lib/api';
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Package,
  Globe,
  Settings,
  BarChart3,
  FileCheck,
} from 'lucide-react';
import Link from 'next/link';

const productCategories = [
  { value: 'electronics', label: 'Electronics' },
  { value: 'software', label: 'Software' },
  { value: 'games', label: 'Games' },
  { value: 'fashion', label: 'Fashion' },
  { value: 'food', label: 'Food & Beverage' },
  { value: 'beauty', label: 'Beauty & Personal Care' },
  { value: 'home', label: 'Home & Garden' },
  { value: 'automotive', label: 'Automotive' },
  { value: 'services', label: 'Services' },
  { value: 'other', label: 'Other' },
];

const projectSchema = z.object({
  // Step 1: Product Info
  product_name: z.string().min(1, 'Product name is required').max(200),
  product_category: z.string().min(1, 'Category is required'),
  product_description: z.string().max(500).optional(),
  product_website: z.string().url().optional().or(z.literal('')),
  competitors: z.string().optional(),

  // Step 2: Platform Links (handled separately)

  // Step 3: Configuration
  scraper_provider: z.string().min(1, 'Scraper provider is required'),
  llm_provider: z.string().min(1, 'LLM provider is required'),
  llm_model: z.string().min(1, 'Model is required'),

  // Step 4: Analysis Options
  analysis_sentiment: z.boolean().default(true),
  analysis_emotions: z.boolean().default(false),
  analysis_summarize: z.boolean().default(false),
  analysis_insights: z.boolean().default(false),
});

type ProjectFormData = z.infer<typeof projectSchema>;

const steps = [
  {
    id: 'product',
    title: 'Product Info',
    description: 'Tell us about your product or brand',
    icon: Package,
  },
  {
    id: 'sources',
    title: 'Data Sources',
    description: 'Configure where to collect feedback',
    icon: Globe,
  },
  {
    id: 'config',
    title: 'Configuration',
    description: 'Scraper and AI settings',
    icon: Settings,
  },
  {
    id: 'analysis',
    title: 'Analysis',
    description: 'Choose analysis options',
    icon: BarChart3,
  },
  {
    id: 'review',
    title: 'Review',
    description: 'Review and create project',
    icon: FileCheck,
  },
];

const scraperProviders = [
  { value: 'scraperapi', label: 'ScraperAPI' },
  { value: 'apify', label: 'Apify' },
  { value: 'scrapingbee', label: 'ScrapingBee' },
];

const emptyPlatformLinks: PlatformLinks = {
  amazon: [],
  steam: [],
  youtube: [],
  reddit: [],
  google: [],
  trustpilot: [],
  yelp: [],
};

export default function NewProjectPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [platformLinks, setPlatformLinks] = useState<PlatformLinks>(emptyPlatformLinks);
  const createProject = useCreateProject();
  const { data: presets } = usePresets();
  const { data: llmProviders } = useLLMProviders();

  const {
    register,
    handleSubmit,
    watch,
    control,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      product_category: 'other',
      scraper_provider: 'scraperapi',
      llm_provider: '',
      llm_model: '',
      analysis_sentiment: true,
      analysis_emotions: false,
      analysis_summarize: false,
      analysis_insights: false,
    },
  });

  const selectedLLMProvider = watch('llm_provider');
  const selectedProvider = llmProviders?.find((p) => p.id === selectedLLMProvider);

  const handlePlatformToggle = (platformId: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platformId)
        ? prev.filter((id) => id !== platformId)
        : [...prev, platformId]
    );
  };

  const onSubmit = async (data: ProjectFormData) => {
    // Build product info
    const product: ProductInfo = {
      name: data.product_name,
      category: data.product_category as ProductInfo['category'],
      description: data.product_description || '',
      website: data.product_website || null,
      competitors: data.competitors
        ? data.competitors.split(',').map((c) => c.trim()).filter(Boolean)
        : [],
    };

    // Filter platform links to only include selected platforms with URLs
    const filteredPlatformLinks: PlatformLinks = {
      amazon: selectedPlatforms.includes('amazon') ? platformLinks.amazon.filter(l => l.url.trim()) : [],
      steam: selectedPlatforms.includes('steam') ? platformLinks.steam.filter(l => l.url.trim()) : [],
      youtube: selectedPlatforms.includes('youtube') ? platformLinks.youtube.filter(l => l.url.trim()) : [],
      reddit: selectedPlatforms.includes('reddit') ? platformLinks.reddit.filter(l => l.url.trim()) : [],
      google: selectedPlatforms.includes('google') ? platformLinks.google.filter(l => l.url.trim()) : [],
      trustpilot: selectedPlatforms.includes('trustpilot') ? platformLinks.trustpilot.filter(l => l.url.trim()) : [],
      yelp: selectedPlatforms.includes('yelp') ? platformLinks.yelp.filter(l => l.url.trim()) : [],
    };

    const payload = {
      name: data.product_name,
      description: data.product_description || `Sentiment analysis for ${data.product_name}`,
      preset: 'custom' as const,
      product,
      platform_links: filteredPlatformLinks,
      config: {
        scrapers: {
          platforms: selectedPlatforms,
          commercial_provider: data.scraper_provider as 'scraperapi' | 'apify' | 'scrapingbee',
        },
        llm: {
          provider: data.llm_provider,
          model: data.llm_model,
        },
        analysis: {
          sentiment: data.analysis_sentiment,
          emotions: data.analysis_emotions,
          summarize: data.analysis_summarize,
          extract_insights: data.analysis_insights,
        },
      },
    };

    try {
      await createProject.mutateAsync(payload);
      router.push('/dashboard/projects');
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canProceed = (): boolean => {
    switch (currentStep) {
      case 0: // Product Info
        return !!watch('product_name') && !!watch('product_category');
      case 1: // Data Sources
        return selectedPlatforms.length > 0;
      case 2: // Configuration
        return !!watch('scraper_provider') && !!watch('llm_provider') && !!watch('llm_model');
      case 3: // Analysis
        return true;
      default:
        return true;
    }
  };

  const getTotalLinks = (): number => {
    return Object.values(platformLinks).reduce(
      (sum, links) => sum + links.filter((l: { url: string }) => l.url.trim()).length,
      0
    );
  };

  const formValues = watch();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/projects">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">New Project</h1>
          <p className="text-sm text-neutral-500">
            Set up sentiment analysis for your product or brand
          </p>
        </div>
      </div>

      {/* Stepper */}
      <div className="flex items-center justify-between px-4">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`flex h-12 w-12 items-center justify-center rounded-full border-2 transition-all ${
                    index < currentStep
                      ? 'border-primary-600 bg-primary-600 text-white'
                      : index === currentStep
                      ? 'border-primary-600 bg-primary-50 text-primary-600'
                      : 'border-neutral-200 bg-white text-neutral-400'
                  }`}
                >
                  {index < currentStep ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                <span
                  className={`mt-2 text-xs font-medium ${
                    index <= currentStep ? 'text-primary-600' : 'text-neutral-400'
                  }`}
                >
                  {step.title}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`h-0.5 w-16 mx-2 ${
                    index < currentStep ? 'bg-primary-600' : 'bg-neutral-200'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Step Content */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {(() => {
              const StepIcon = steps[currentStep].icon;
              return <StepIcon className="h-5 w-5 text-primary-600" />;
            })()}
            {steps[currentStep].title}
          </CardTitle>
          <CardDescription>{steps[currentStep].description}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Step 1: Product Info */}
            {currentStep === 0 && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="product_name" required>
                    Product / Brand Name
                  </Label>
                  <Input
                    id="product_name"
                    placeholder="e.g., iPhone 15 Pro, Nike Air Max, Spotify"
                    error={!!errors.product_name}
                    {...register('product_name')}
                  />
                  {errors.product_name && (
                    <p className="mt-1 text-sm text-error-600">
                      {errors.product_name.message}
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="product_category" required>
                    Category
                  </Label>
                  <Select
                    options={productCategories}
                    error={!!errors.product_category}
                    {...register('product_category')}
                  />
                </div>

                <div>
                  <Label htmlFor="product_description">Description</Label>
                  <Textarea
                    id="product_description"
                    placeholder="Brief description of your product or brand..."
                    rows={3}
                    {...register('product_description')}
                  />
                </div>

                <div>
                  <Label htmlFor="product_website">Official Website (Optional)</Label>
                  <Input
                    id="product_website"
                    type="url"
                    placeholder="https://www.example.com"
                    {...register('product_website')}
                  />
                </div>

                <div>
                  <Label htmlFor="competitors">Competitors (Optional)</Label>
                  <Input
                    id="competitors"
                    placeholder="Samsung Galaxy, Google Pixel (comma separated)"
                    {...register('competitors')}
                  />
                  <p className="mt-1 text-sm text-neutral-500">
                    Add competitor names to compare sentiment analysis
                  </p>
                </div>
              </div>
            )}

            {/* Step 2: Data Sources */}
            {currentStep === 1 && (
              <PlatformLinksInput
                value={platformLinks}
                onChange={setPlatformLinks}
                selectedPlatforms={selectedPlatforms}
                onPlatformToggle={handlePlatformToggle}
              />
            )}

            {/* Step 3: Configuration */}
            {currentStep === 2 && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="scraper_provider" required>
                    Scraper Provider
                  </Label>
                  <Select
                    options={scraperProviders}
                    error={!!errors.scraper_provider}
                    {...register('scraper_provider')}
                  />
                  <p className="mt-1 text-sm text-neutral-500">
                    Commercial scraping service for reliable data collection
                  </p>
                </div>

                <div>
                  <Label htmlFor="llm_provider" required>
                    AI Provider
                  </Label>
                  <Select
                    options={
                      llmProviders?.map((p) => ({ value: p.id, label: p.name })) || []
                    }
                    error={!!errors.llm_provider}
                    {...register('llm_provider')}
                  />
                </div>

                {selectedProvider && (
                  <div>
                    <Label htmlFor="llm_model" required>
                      AI Model
                    </Label>
                    <Select
                      options={selectedProvider.models.map((m) => ({
                        value: m.id,
                        label: m.name,
                      }))}
                      error={!!errors.llm_model}
                      {...register('llm_model')}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Step 4: Analysis Options */}
            {currentStep === 3 && (
              <div className="space-y-4">
                <Alert variant="info">
                  Select what type of analysis to perform on collected reviews and
                  comments.
                </Alert>
                <Checkbox
                  label="Sentiment Analysis"
                  description="Detect positive, negative, neutral, or mixed sentiment"
                  {...register('analysis_sentiment')}
                />
                <Checkbox
                  label="Emotion Detection"
                  description="Identify emotions like joy, sadness, anger, fear, surprise"
                  {...register('analysis_emotions')}
                />
                <Checkbox
                  label="Summary Generation"
                  description="Generate brief summaries of reviews and feedback"
                  {...register('analysis_summarize')}
                />
                <Checkbox
                  label="Extract Insights"
                  description="Extract key themes, pros/cons, and actionable insights"
                  {...register('analysis_insights')}
                />
              </div>
            )}

            {/* Step 5: Review */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <div className="rounded-lg bg-neutral-50 p-6 space-y-4">
                  <h3 className="font-semibold text-neutral-900 border-b pb-2">
                    Product Information
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-neutral-500">Name</span>
                      <p className="font-medium">{formValues.product_name || '-'}</p>
                    </div>
                    <div>
                      <span className="text-sm text-neutral-500">Category</span>
                      <p className="font-medium">
                        {productCategories.find(
                          (c) => c.value === formValues.product_category
                        )?.label || '-'}
                      </p>
                    </div>
                    {formValues.product_website && (
                      <div className="col-span-2">
                        <span className="text-sm text-neutral-500">Website</span>
                        <p className="font-medium">{formValues.product_website}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="rounded-lg bg-neutral-50 p-6 space-y-4">
                  <h3 className="font-semibold text-neutral-900 border-b pb-2">
                    Data Sources
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedPlatforms.map((platformId) => {
                      const platform = PLATFORMS.find((p) => p.id === platformId);
                      const linkCount = platformLinks[
                        platformId as keyof PlatformLinks
                      ]?.filter((l) => l.url.trim()).length || 0;
                      return (
                        <span
                          key={platformId}
                          className="inline-flex items-center gap-1 rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700"
                        >
                          {platform?.name}
                          {linkCount > 0 && (
                            <span className="ml-1 rounded-full bg-primary-200 px-1.5 text-xs">
                              {linkCount}
                            </span>
                          )}
                        </span>
                      );
                    })}
                  </div>
                  <p className="text-sm text-neutral-500">
                    {getTotalLinks()} total links configured
                  </p>
                </div>

                <div className="rounded-lg bg-neutral-50 p-6 space-y-4">
                  <h3 className="font-semibold text-neutral-900 border-b pb-2">
                    Configuration
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-neutral-500">Scraper</span>
                      <p className="font-medium">
                        {scraperProviders.find(
                          (s) => s.value === formValues.scraper_provider
                        )?.label || '-'}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm text-neutral-500">AI Model</span>
                      <p className="font-medium">
                        {selectedProvider?.models.find(
                          (m) => m.id === formValues.llm_model
                        )?.name || '-'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-lg bg-neutral-50 p-6 space-y-4">
                  <h3 className="font-semibold text-neutral-900 border-b pb-2">
                    Analysis Options
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {formValues.analysis_sentiment && (
                      <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
                        Sentiment
                      </span>
                    )}
                    {formValues.analysis_emotions && (
                      <span className="rounded-full bg-purple-100 px-3 py-1 text-sm font-medium text-purple-700">
                        Emotions
                      </span>
                    )}
                    {formValues.analysis_summarize && (
                      <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
                        Summary
                      </span>
                    )}
                    {formValues.analysis_insights && (
                      <span className="rounded-full bg-amber-100 px-3 py-1 text-sm font-medium text-amber-700">
                        Insights
                      </span>
                    )}
                    {!formValues.analysis_sentiment &&
                      !formValues.analysis_emotions &&
                      !formValues.analysis_summarize &&
                      !formValues.analysis_insights && (
                        <span className="text-neutral-500">
                          No analysis options selected
                        </span>
                      )}
                  </div>
                </div>
              </div>
            )}

            {/* Navigation */}
            <div className="space-y-4">
              {Object.keys(errors).length > 0 && (
                <Alert variant="error">
                  <div className="space-y-1">
                    <p className="font-medium">Please fix the following errors:</p>
                    <ul className="list-disc list-inside text-sm">
                      {Object.entries(errors).map(([field, error]) => (
                        <li key={field}>
                          {field.replace(/_/g, ' ')}: {error?.message}
                        </li>
                      ))}
                    </ul>
                  </div>
                </Alert>
              )}

              <div className="flex justify-between pt-4 border-t">
                <Button
                  type="button"
                  variant="outline"
                  onClick={prevStep}
                  disabled={currentStep === 0}
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Previous
                </Button>
                {currentStep < steps.length - 1 ? (
                  <Button
                    type="button"
                    onClick={nextStep}
                    disabled={!canProceed()}
                  >
                    Next
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                ) : (
                  <Button type="submit" isLoading={createProject.isPending}>
                    Create Project
                  </Button>
                )}
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
