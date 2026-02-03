'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  StatusBadge,
  SentimentBadge,
  Badge,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  TableEmpty,
  TableLoading,
  Pagination,
  PaginationInfo,
  ConfirmModal,
  Modal,
  ModalFooter,
  Input,
  Textarea,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  Alert,
  SkeletonStats,
} from '@/components/ui';
import {
  useProject,
  useProjectStats,
  useTargets,
  useAddTarget,
  useAddTargetsBulk,
  useDeleteTarget,
  useResults,
  useStartScrape,
  useScrapeJobs,
  useExportResults,
  useDeleteProject,
} from '@/hooks';
import { formatDate, formatRelativeTime, formatNumber, formatPercent } from '@/lib/utils';
import {
  ArrowLeft,
  Play,
  Download,
  Plus,
  Trash2,
  ExternalLink,
  Globe,
  TrendingUp,
  FileText,
  Target,
  Settings,
  RefreshCw,
} from 'lucide-react';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [resultsPage, setResultsPage] = useState(1);
  const [showAddTarget, setShowAddTarget] = useState(false);
  const [targetUrls, setTargetUrls] = useState('');
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [showDeleteProject, setShowDeleteProject] = useState(false);
  const [exportFormat, setExportFormat] = useState<'csv' | 'json' | 'xlsx'>('csv');

  const { data: project, isLoading: projectLoading } = useProject(projectId);
  const { data: stats, isLoading: statsLoading } = useProjectStats(projectId);
  const { data: targets, isLoading: targetsLoading } = useTargets(projectId);
  const { data: results, isLoading: resultsLoading } = useResults(projectId, {
    page: resultsPage,
    limit: 10,
  });
  const { data: jobs } = useScrapeJobs(projectId);

  const addTargetsBulk = useAddTargetsBulk();
  const deleteTarget = useDeleteTarget();
  const startScrape = useStartScrape();
  const exportResults = useExportResults();
  const deleteProject = useDeleteProject();

  const handleAddTargets = async () => {
    const urls = targetUrls
      .split('\n')
      .map((url) => url.trim())
      .filter((url) => url.length > 0);

    if (urls.length > 0) {
      await addTargetsBulk.mutateAsync({ projectId, urls });
      setShowAddTarget(false);
      setTargetUrls('');
    }
  };

  const handleDeleteTarget = async () => {
    if (deleteTargetId) {
      await deleteTarget.mutateAsync({ projectId, targetId: deleteTargetId });
      setDeleteTargetId(null);
    }
  };

  const handleStartScrape = async () => {
    await startScrape.mutateAsync(projectId);
  };

  const handleExport = async () => {
    await exportResults.mutateAsync({ projectId, format: exportFormat });
  };

  const handleDeleteProject = async () => {
    await deleteProject.mutateAsync(projectId);
    router.push('/dashboard/projects');
  };

  const runningJob = jobs?.find((j) => j.status === 'running' || j.status === 'pending');

  if (projectLoading) {
    return (
      <div className="space-y-6">
        <SkeletonStats />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-neutral-900">Project not found</h2>
        <p className="mt-2 text-neutral-500">
          The project you're looking for doesn't exist or has been deleted.
        </p>
        <Link href="/dashboard/projects">
          <Button variant="outline" className="mt-4">
            Back to Projects
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard/projects">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-neutral-900">{project.name}</h1>
              <StatusBadge status={project.status} />
            </div>
            {project.description && (
              <p className="mt-1 text-sm text-neutral-500">{project.description}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={handleStartScrape}
            disabled={startScrape.isPending || !!runningJob || !targets?.length}
            isLoading={startScrape.isPending}
          >
            {runningJob ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Start Scrape
              </>
            )}
          </Button>
          <Button
            variant="outline"
            onClick={handleExport}
            disabled={exportResults.isPending || !results?.total}
            isLoading={exportResults.isPending}
          >
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Running Job Alert */}
      {runningJob && (
        <Alert variant="info">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span>
            Scrape job in progress: {runningJob.progress}% complete
            {runningJob.stats && ` (${runningJob.stats.results_scraped} results)`}
          </span>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-primary-100 p-2">
                <Target className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <p className="text-sm text-neutral-500">Targets</p>
                <p className="text-2xl font-bold text-neutral-900">
                  {targets?.length || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-success-100 p-2">
                <FileText className="h-5 w-5 text-success-600" />
              </div>
              <div>
                <p className="text-sm text-neutral-500">Results</p>
                <p className="text-2xl font-bold text-neutral-900">
                  {formatNumber(results?.total || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-warning-100 p-2">
                <TrendingUp className="h-5 w-5 text-warning-600" />
              </div>
              <div>
                <p className="text-sm text-neutral-500">Avg. Sentiment</p>
                <p className="text-2xl font-bold text-neutral-900">
                  {stats?.avg_sentiment_score
                    ? formatPercent(stats.avg_sentiment_score)
                    : '-'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-neutral-100 p-2">
                <Globe className="h-5 w-5 text-neutral-600" />
              </div>
              <div>
                <p className="text-sm text-neutral-500">Last Scrape</p>
                <p className="text-lg font-bold text-neutral-900">
                  {project.stats?.last_scrape_at
                    ? formatRelativeTime(project.stats.last_scrape_at)
                    : 'Never'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="results">
        <TabsList>
          <TabsTrigger value="results">Results</TabsTrigger>
          <TabsTrigger value="targets">Targets</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Results Tab */}
        <TabsContent value="results">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Content</TableHead>
                  <TableHead>Platform</TableHead>
                  <TableHead>Sentiment</TableHead>
                  <TableHead>Rating</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {resultsLoading ? (
                  <TableLoading colSpan={5} rows={5} />
                ) : !results?.items?.length ? (
                  <TableEmpty colSpan={5} message="No results yet. Start a scrape to collect data." />
                ) : (
                  results.items.map((result) => (
                    <TableRow key={result.id}>
                      <TableCell className="max-w-md">
                        <div className="truncate">
                          {result.content.title && (
                            <div className="font-medium">{result.content.title}</div>
                          )}
                          <div className="text-sm text-neutral-500 truncate">
                            {result.content.text}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge>{result.platform}</Badge>
                      </TableCell>
                      <TableCell>
                        <SentimentBadge
                          sentiment={result.analysis.sentiment.label as any}
                          score={result.analysis.sentiment.confidence}
                        />
                      </TableCell>
                      <TableCell>
                        {result.content.rating ? `${result.content.rating}/5` : '-'}
                      </TableCell>
                      <TableCell>
                        {result.content.date ? formatDate(result.content.date) : '-'}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
            {results && results.pages > 1 && (
              <div className="flex items-center justify-between border-t border-neutral-200 px-4 py-3">
                <PaginationInfo
                  currentPage={resultsPage}
                  pageSize={10}
                  totalItems={results.total}
                />
                <Pagination
                  currentPage={resultsPage}
                  totalPages={results.pages}
                  onPageChange={setResultsPage}
                />
              </div>
            )}
          </Card>
        </TabsContent>

        {/* Targets Tab */}
        <TabsContent value="targets">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Targets</CardTitle>
              <Button onClick={() => setShowAddTarget(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Targets
              </Button>
            </CardHeader>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>URL</TableHead>
                  <TableHead>Platform</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Scraped</TableHead>
                  <TableHead className="w-[80px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {targetsLoading ? (
                  <TableLoading colSpan={5} rows={5} />
                ) : !targets?.length ? (
                  <TableEmpty colSpan={5} message="No targets added yet." />
                ) : (
                  targets.map((target) => (
                    <TableRow key={target.id}>
                      <TableCell>
                        <div className="flex items-center gap-2 max-w-md">
                          <span className="truncate">{target.url}</span>
                          <a
                            href={target.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-neutral-400 hover:text-neutral-600"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge>{target.platform}</Badge>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={target.status} />
                      </TableCell>
                      <TableCell>
                        {target.last_scraped_at
                          ? formatRelativeTime(target.last_scraped_at)
                          : '-'}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-error-600"
                          onClick={() => setDeleteTargetId(target.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Project Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-neutral-500">Scraper Provider</p>
                  <p className="font-medium">{project.config.scraper.provider}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">LLM Provider</p>
                  <p className="font-medium">{project.config.llm.provider}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Model</p>
                  <p className="font-medium">{project.config.llm.model}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Created</p>
                  <p className="font-medium">{formatDate(project.created_at)}</p>
                </div>
              </div>

              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold text-error-600 mb-4">Danger Zone</h3>
                <Button
                  variant="destructive"
                  onClick={() => setShowDeleteProject(true)}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete Project
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add Targets Modal */}
      <Modal
        isOpen={showAddTarget}
        onClose={() => setShowAddTarget(false)}
        title="Add Targets"
        size="lg"
      >
        <div className="space-y-4">
          <p className="text-sm text-neutral-500">
            Enter URLs to analyze, one per line.
          </p>
          <Textarea
            value={targetUrls}
            onChange={(e) => setTargetUrls(e.target.value)}
            placeholder="https://www.amazon.com/product/...&#10;https://www.trustpilot.com/review/..."
            rows={8}
          />
        </div>
        <ModalFooter>
          <Button variant="outline" onClick={() => setShowAddTarget(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleAddTargets}
            isLoading={addTargetsBulk.isPending}
            disabled={!targetUrls.trim()}
          >
            Add Targets
          </Button>
        </ModalFooter>
      </Modal>

      {/* Delete Target Modal */}
      <ConfirmModal
        isOpen={!!deleteTargetId}
        onClose={() => setDeleteTargetId(null)}
        onConfirm={handleDeleteTarget}
        title="Delete Target"
        message="Are you sure you want to delete this target?"
        confirmText="Delete"
        variant="danger"
        isLoading={deleteTarget.isPending}
      />

      {/* Delete Project Modal */}
      <ConfirmModal
        isOpen={showDeleteProject}
        onClose={() => setShowDeleteProject(false)}
        onConfirm={handleDeleteProject}
        title="Delete Project"
        message="Are you sure you want to delete this project? All data including targets and results will be permanently deleted."
        confirmText="Delete Project"
        variant="danger"
        isLoading={deleteProject.isPending}
      />
    </div>
  );
}
