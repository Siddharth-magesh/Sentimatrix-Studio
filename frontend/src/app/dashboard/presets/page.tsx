'use client';

import { useState } from 'react';
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
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  TableEmpty,
  TableLoading,
  Modal,
  ModalFooter,
  ConfirmModal,
  Badge,
  Alert,
} from '@/components/ui';
import {
  usePresets,
  usePreset,
  useCreatePreset,
  useUpdatePreset,
  useDeletePreset,
  useLLMProviders,
} from '@/hooks';
import { formatDate } from '@/lib/utils';
import { Plus, Edit, Trash2, Copy, Settings2, Zap } from 'lucide-react';

const presetSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  description: z.string().max(500, 'Description too long').optional(),
  is_default: z.boolean().default(false),
  scraper_provider: z.string().min(1, 'Scraper provider is required'),
  llm_provider: z.string().min(1, 'LLM provider is required'),
  llm_model: z.string().min(1, 'Model is required'),
  analysis_sentiment: z.boolean().default(true),
  analysis_emotions: z.boolean().default(false),
  analysis_keywords: z.boolean().default(false),
  analysis_summary: z.boolean().default(false),
});

type PresetFormData = z.infer<typeof presetSchema>;

const scraperProviders = [
  { value: 'scraperapi', label: 'ScraperAPI' },
  { value: 'apify', label: 'Apify' },
  { value: 'brightdata', label: 'Bright Data' },
  { value: 'scrapingbee', label: 'ScrapingBee' },
];

export default function PresetsPage() {
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const { data: presets, isLoading } = usePresets();
  const { data: llmProviders } = useLLMProviders();
  const createPreset = useCreatePreset();
  const updatePreset = useUpdatePreset();
  const deletePreset = useDeletePreset();

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<PresetFormData>({
    resolver: zodResolver(presetSchema),
    defaultValues: {
      analysis_sentiment: true,
      analysis_emotions: false,
      analysis_keywords: false,
      analysis_summary: false,
      is_default: false,
    },
  });

  const selectedLLMProvider = watch('llm_provider');
  const selectedProvider = llmProviders?.find((p) => p.id === selectedLLMProvider);

  const openModal = (preset?: any) => {
    if (preset) {
      setEditId(preset.id);
      reset({
        name: preset.name,
        description: preset.description || '',
        is_default: preset.is_default,
        scraper_provider: preset.config.scraper.provider,
        llm_provider: preset.config.llm.provider,
        llm_model: preset.config.llm.model,
        analysis_sentiment: preset.config.analysis?.sentiment ?? true,
        analysis_emotions: preset.config.analysis?.emotions ?? false,
        analysis_keywords: preset.config.analysis?.keywords ?? false,
        analysis_summary: preset.config.analysis?.summary ?? false,
      });
    } else {
      setEditId(null);
      reset({
        name: '',
        description: '',
        is_default: false,
        scraper_provider: '',
        llm_provider: '',
        llm_model: '',
        analysis_sentiment: true,
        analysis_emotions: false,
        analysis_keywords: false,
        analysis_summary: false,
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditId(null);
    reset();
  };

  const onSubmit = async (data: PresetFormData) => {
    const payload = {
      name: data.name,
      description: data.description,
      is_default: data.is_default,
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
    };

    if (editId) {
      await updatePreset.mutateAsync({ id: editId, ...payload });
    } else {
      await createPreset.mutateAsync(payload);
    }
    closeModal();
  };

  const handleDelete = async () => {
    if (deleteId) {
      await deletePreset.mutateAsync(deleteId);
      setDeleteId(null);
    }
  };

  const handleDuplicate = (preset: any) => {
    reset({
      name: `${preset.name} (Copy)`,
      description: preset.description || '',
      is_default: false,
      scraper_provider: preset.config.scraper.provider,
      llm_provider: preset.config.llm.provider,
      llm_model: preset.config.llm.model,
      analysis_sentiment: preset.config.analysis?.sentiment ?? true,
      analysis_emotions: preset.config.analysis?.emotions ?? false,
      analysis_keywords: preset.config.analysis?.keywords ?? false,
      analysis_summary: preset.config.analysis?.summary ?? false,
    });
    setEditId(null);
    setShowModal(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Presets</h1>
          <p className="text-sm text-neutral-500">
            Save and reuse project configurations
          </p>
        </div>
        <Button onClick={() => openModal()}>
          <Plus className="mr-2 h-4 w-4" />
          New Preset
        </Button>
      </div>

      {/* Info Alert */}
      <Alert variant="info">
        <Zap className="h-4 w-4" />
        <span>
          Presets let you quickly configure new projects with your preferred settings.
          Mark a preset as default to auto-select it when creating new projects.
        </span>
      </Alert>

      {/* Presets Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Preset</TableHead>
              <TableHead>Scraper</TableHead>
              <TableHead>LLM</TableHead>
              <TableHead>Analysis</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-[120px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableLoading colSpan={6} rows={5} />
            ) : !presets?.length ? (
              <TableEmpty
                colSpan={6}
                message="No presets yet. Create your first preset to save project configurations."
              />
            ) : (
              presets.map((preset) => (
                <TableRow key={preset.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div>
                        <div className="font-medium text-neutral-900 flex items-center gap-2">
                          {preset.name}
                          {preset.is_default && (
                            <Badge variant="primary" size="sm">Default</Badge>
                          )}
                        </div>
                        {preset.description && (
                          <div className="text-sm text-neutral-500 truncate max-w-xs">
                            {preset.description}
                          </div>
                        )}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge>{preset.config.scraper.provider}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div className="font-medium">{preset.config.llm.provider}</div>
                      <div className="text-neutral-500">{preset.config.llm.model}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {preset.config.analysis?.sentiment && (
                        <Badge variant="success" size="sm">Sentiment</Badge>
                      )}
                      {preset.config.analysis?.emotions && (
                        <Badge variant="warning" size="sm">Emotions</Badge>
                      )}
                      {preset.config.analysis?.keywords && (
                        <Badge variant="info" size="sm">Keywords</Badge>
                      )}
                      {preset.config.analysis?.summary && (
                        <Badge variant="neutral" size="sm">Summary</Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{formatDate(preset.created_at)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={() => openModal(preset)}
                        title="Edit"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={() => handleDuplicate(preset)}
                        title="Duplicate"
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0 text-error-600 hover:text-error-700"
                        onClick={() => setDeleteId(preset.id)}
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={editId ? 'Edit Preset' : 'New Preset'}
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="name" required>Preset Name</Label>
              <Input
                id="name"
                placeholder="My Analysis Preset"
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
                placeholder="Describe this preset..."
                rows={2}
                {...register('description')}
              />
            </div>
            <Checkbox
              label="Set as default preset"
              description="This preset will be auto-selected when creating new projects"
              {...register('is_default')}
            />
          </div>

          {/* Configuration */}
          <div className="border-t pt-4 space-y-4">
            <h3 className="font-medium text-neutral-900 flex items-center gap-2">
              <Settings2 className="h-4 w-4" />
              Configuration
            </h3>
            <div className="grid gap-4 sm:grid-cols-2">
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
                  options={llmProviders?.map((p) => ({ value: p.id, label: p.name })) || []}
                  error={!!errors.llm_provider}
                  {...register('llm_provider')}
                />
                {errors.llm_provider && (
                  <p className="mt-1 text-sm text-error-600">{errors.llm_provider.message}</p>
                )}
              </div>
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

          {/* Analysis Options */}
          <div className="border-t pt-4 space-y-4">
            <h3 className="font-medium text-neutral-900">Analysis Options</h3>
            <div className="grid gap-4 sm:grid-cols-2">
              <Checkbox
                label="Sentiment Analysis"
                description="Positive/negative/neutral detection"
                {...register('analysis_sentiment')}
              />
              <Checkbox
                label="Emotion Detection"
                description="Joy, sadness, anger, fear"
                {...register('analysis_emotions')}
              />
              <Checkbox
                label="Keyword Extraction"
                description="Key topics and themes"
                {...register('analysis_keywords')}
              />
              <Checkbox
                label="Summary Generation"
                description="Brief content summaries"
                {...register('analysis_summary')}
              />
            </div>
          </div>

          <ModalFooter>
            <Button type="button" variant="outline" onClick={closeModal}>
              Cancel
            </Button>
            <Button
              type="submit"
              isLoading={createPreset.isPending || updatePreset.isPending}
            >
              {editId ? 'Update Preset' : 'Create Preset'}
            </Button>
          </ModalFooter>
        </form>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmModal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={handleDelete}
        title="Delete Preset"
        message="Are you sure you want to delete this preset? This action cannot be undone."
        confirmText="Delete"
        variant="danger"
        isLoading={deletePreset.isPending}
      />
    </div>
  );
}
