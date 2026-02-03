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
import { useCreateProject, usePresets, useLLMProviders } from '@/hooks';
import { ArrowLeft, ArrowRight, Check, Loader2 } from 'lucide-react';
import Link from 'next/link';

const projectSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  description: z.string().max(500, 'Description too long').optional(),
  preset_id: z.string().optional(),
  scraper_provider: z.string().min(1, 'Scraper provider is required'),
  llm_provider: z.string().min(1, 'LLM provider is required'),
  llm_model: z.string().min(1, 'Model is required'),
  analysis_sentiment: z.boolean().default(true),
  analysis_emotions: z.boolean().default(false),
  analysis_keywords: z.boolean().default(false),
  analysis_summary: z.boolean().default(false),
  targets: z.string().optional(),
});

type ProjectFormData = z.infer<typeof projectSchema>;

const steps = [
  { id: 'basic', title: 'Basic Info', description: 'Project name and description' },
  { id: 'config', title: 'Configuration', description: 'Scraper and LLM settings' },
  { id: 'analysis', title: 'Analysis', description: 'Analysis options' },
  { id: 'targets', title: 'Targets', description: 'Add URLs to analyze' },
  { id: 'review', title: 'Review', description: 'Review and create' },
];

const scraperProviders = [
  { value: 'scraperapi', label: 'ScraperAPI' },
  { value: 'apify', label: 'Apify' },
  { value: 'brightdata', label: 'Bright Data' },
  { value: 'scrapingbee', label: 'ScrapingBee' },
];

export default function NewProjectPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const createProject = useCreateProject();
  const { data: presets } = usePresets();
  const { data: llmProviders } = useLLMProviders();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      analysis_sentiment: true,
      analysis_emotions: false,
      analysis_keywords: false,
      analysis_summary: false,
    },
  });

  const selectedLLMProvider = watch('llm_provider');
  const selectedProvider = llmProviders?.find((p) => p.id === selectedLLMProvider);

  const onSubmit = async (data: ProjectFormData) => {
    const targets = data.targets
      ?.split('\n')
      .map((url) => url.trim())
      .filter((url) => url.length > 0);

    await createProject.mutateAsync({
      name: data.name,
      description: data.description,
      preset_id: data.preset_id,
      config: {
        scraper: {
          provider: data.scraper_provider,
        },
        llm: {
          provider: data.llm_provider,
          model: data.llm_model,
        },
        analysis: {
          sentiment: data.analysis_sentiment,
          emotions: data.analysis_emotions,
          keywords: data.analysis_keywords,
          summary: data.analysis_summary,
        },
      },
    });

    router.push('/dashboard/projects');
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

  const formValues = watch();

  return (
    <div className="max-w-3xl mx-auto space-y-6">
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
            Create a new sentiment analysis project
          </p>
        </div>
      </div>

      {/* Stepper */}
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
                index < currentStep
                  ? 'border-primary-600 bg-primary-600 text-white'
                  : index === currentStep
                  ? 'border-primary-600 text-primary-600'
                  : 'border-neutral-300 text-neutral-400'
              }`}
            >
              {index < currentStep ? (
                <Check className="h-5 w-5" />
              ) : (
                <span>{index + 1}</span>
              )}
            </div>
            {index < steps.length - 1 && (
              <div
                className={`h-0.5 w-12 sm:w-20 ${
                  index < currentStep ? 'bg-primary-600' : 'bg-neutral-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <Card>
        <CardHeader>
          <CardTitle>{steps[currentStep].title}</CardTitle>
          <CardDescription>{steps[currentStep].description}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Step 1: Basic Info */}
            {currentStep === 0 && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name" required>Project Name</Label>
                  <Input
                    id="name"
                    placeholder="My Analysis Project"
                    error={!!errors.name}
                    {...register('name')}
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-error-600">{errors.name.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe what this project is for..."
                    rows={3}
                    {...register('description')}
                  />
                </div>
                {presets && presets.length > 0 && (
                  <div>
                    <Label htmlFor="preset_id">Use Preset (Optional)</Label>
                    <Select
                      options={[
                        { value: '', label: 'No preset' },
                        ...presets.map((p) => ({ value: p.id, label: p.name })),
                      ]}
                      {...register('preset_id')}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Configuration */}
            {currentStep === 1 && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="scraper_provider" required>Scraper Provider</Label>
                  <Select
                    options={scraperProviders}
                    error={!!errors.scraper_provider}
                    {...register('scraper_provider')}
                  />
                  {errors.scraper_provider && (
                    <p className="mt-1 text-sm text-error-600">{errors.scraper_provider.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="llm_provider" required>LLM Provider</Label>
                  <Select
                    options={
                      llmProviders?.map((p) => ({ value: p.id, label: p.name })) || []
                    }
                    error={!!errors.llm_provider}
                    {...register('llm_provider')}
                  />
                  {errors.llm_provider && (
                    <p className="mt-1 text-sm text-error-600">{errors.llm_provider.message}</p>
                  )}
                </div>
                {selectedProvider && (
                  <div>
                    <Label htmlFor="llm_model" required>Model</Label>
                    <Select
                      options={selectedProvider.models.map((m) => ({
                        value: m.id,
                        label: m.name,
                      }))}
                      error={!!errors.llm_model}
                      {...register('llm_model')}
                    />
                    {errors.llm_model && (
                      <p className="mt-1 text-sm text-error-600">{errors.llm_model.message}</p>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Step 3: Analysis Options */}
            {currentStep === 2 && (
              <div className="space-y-4">
                <Alert variant="info">
                  Select what type of analysis to perform on scraped content.
                </Alert>
                <Checkbox
                  label="Sentiment Analysis"
                  description="Detect positive, negative, neutral, or mixed sentiment"
                  {...register('analysis_sentiment')}
                />
                <Checkbox
                  label="Emotion Detection"
                  description="Identify emotions like joy, sadness, anger, fear"
                  {...register('analysis_emotions')}
                />
                <Checkbox
                  label="Keyword Extraction"
                  description="Extract key topics and themes"
                  {...register('analysis_keywords')}
                />
                <Checkbox
                  label="Summary Generation"
                  description="Generate brief summaries of content"
                  {...register('analysis_summary')}
                />
              </div>
            )}

            {/* Step 4: Targets */}
            {currentStep === 3 && (
              <div className="space-y-4">
                <Alert variant="info">
                  Enter URLs to analyze, one per line. You can also add targets later.
                </Alert>
                <div>
                  <Label htmlFor="targets">Target URLs</Label>
                  <Textarea
                    id="targets"
                    placeholder="https://www.amazon.com/product/...&#10;https://www.trustpilot.com/review/...&#10;https://www.yelp.com/biz/..."
                    rows={8}
                    {...register('targets')}
                  />
                  <p className="mt-1 text-sm text-neutral-500">
                    Supported: Amazon, Steam, YouTube, Reddit, Google, Trustpilot, Yelp
                  </p>
                </div>
              </div>
            )}

            {/* Step 5: Review */}
            {currentStep === 4 && (
              <div className="space-y-4">
                <div className="rounded-lg bg-neutral-50 p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Project Name</span>
                    <span className="font-medium">{formValues.name || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Scraper</span>
                    <span className="font-medium">{formValues.scraper_provider || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">LLM Provider</span>
                    <span className="font-medium">{formValues.llm_provider || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Model</span>
                    <span className="font-medium">{formValues.llm_model || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Analysis</span>
                    <span className="font-medium">
                      {[
                        formValues.analysis_sentiment && 'Sentiment',
                        formValues.analysis_emotions && 'Emotions',
                        formValues.analysis_keywords && 'Keywords',
                        formValues.analysis_summary && 'Summary',
                      ]
                        .filter(Boolean)
                        .join(', ') || 'None'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Targets</span>
                    <span className="font-medium">
                      {formValues.targets?.split('\n').filter((t) => t.trim()).length || 0} URLs
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Navigation */}
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
                <Button type="button" onClick={nextStep}>
                  Next
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button type="submit" isLoading={createProject.isPending}>
                  Create Project
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
