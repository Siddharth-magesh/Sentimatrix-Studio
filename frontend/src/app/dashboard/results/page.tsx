'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Input,
  Select,
  Badge,
  StatusBadge,
  SentimentBadge,
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
  Alert,
} from '@/components/ui';
import {
  useProjects,
  useResults,
  useExportResults,
  useDeleteResult,
} from '@/hooks';
import { formatDate, formatRelativeTime } from '@/lib/utils';
import {
  Search,
  Download,
  Filter,
  ExternalLink,
  Trash2,
  Eye,
  X,
  FileText,
  BarChart3,
} from 'lucide-react';

interface ResultFilters {
  project_id?: string;
  sentiment?: string;
  platform?: string;
  search?: string;
}

export default function ResultsPage() {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<ResultFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const [selectedResult, setSelectedResult] = useState<any | null>(null);
  const [deleteResultId, setDeleteResultId] = useState<string | null>(null);
  const [exportFormat, setExportFormat] = useState<'csv' | 'json' | 'xlsx'>('csv');

  // Fetch projects for filter dropdown
  const { data: projectsData } = useProjects({ limit: 100 });

  // Fetch results with filters
  const { data: results, isLoading } = useResults(filters.project_id || 'all', {
    page,
    limit: 20,
    sentiment: filters.sentiment,
    platform: filters.platform,
    search: filters.search,
  });

  const exportResults = useExportResults();
  const deleteResult = useDeleteResult();

  const handleExport = async () => {
    if (filters.project_id) {
      await exportResults.mutateAsync({
        projectId: filters.project_id,
        format: exportFormat,
      });
    }
  };

  const handleDeleteResult = async () => {
    if (deleteResultId && filters.project_id) {
      await deleteResult.mutateAsync({
        projectId: filters.project_id,
        resultId: deleteResultId,
      });
      setDeleteResultId(null);
    }
  };

  const clearFilters = () => {
    setFilters({});
    setPage(1);
  };

  const hasActiveFilters = filters.sentiment || filters.platform || filters.search;

  const sentimentOptions = [
    { value: '', label: 'All Sentiments' },
    { value: 'positive', label: 'Positive' },
    { value: 'negative', label: 'Negative' },
    { value: 'neutral', label: 'Neutral' },
    { value: 'mixed', label: 'Mixed' },
  ];

  const platformOptions = [
    { value: '', label: 'All Platforms' },
    { value: 'amazon', label: 'Amazon' },
    { value: 'youtube', label: 'YouTube' },
    { value: 'reddit', label: 'Reddit' },
    { value: 'trustpilot', label: 'Trustpilot' },
    { value: 'yelp', label: 'Yelp' },
    { value: 'steam', label: 'Steam' },
    { value: 'google', label: 'Google' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Results</h1>
          <p className="text-sm text-neutral-500">
            Browse and analyze sentiment results across all projects
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="mr-2 h-4 w-4" />
            Filters
            {hasActiveFilters && (
              <Badge variant="primary" size="sm" className="ml-2">
                Active
              </Badge>
            )}
          </Button>
          {filters.project_id && (
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={exportResults.isPending || !results?.total}
              isLoading={exportResults.isPending}
            >
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          )}
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <Card>
          <CardContent className="py-4">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {/* Project Filter */}
              <div>
                <label className="text-sm font-medium text-neutral-700 mb-1 block">
                  Project
                </label>
                <Select
                  value={filters.project_id || ''}
                  onChange={(e) => {
                    setFilters({ ...filters, project_id: e.target.value || undefined });
                    setPage(1);
                  }}
                  options={[
                    { value: '', label: 'All Projects' },
                    ...(projectsData?.items?.map((p) => ({
                      value: p.id,
                      label: p.name,
                    })) || []),
                  ]}
                />
              </div>

              {/* Sentiment Filter */}
              <div>
                <label className="text-sm font-medium text-neutral-700 mb-1 block">
                  Sentiment
                </label>
                <Select
                  value={filters.sentiment || ''}
                  onChange={(e) => {
                    setFilters({ ...filters, sentiment: e.target.value || undefined });
                    setPage(1);
                  }}
                  options={sentimentOptions}
                />
              </div>

              {/* Platform Filter */}
              <div>
                <label className="text-sm font-medium text-neutral-700 mb-1 block">
                  Platform
                </label>
                <Select
                  value={filters.platform || ''}
                  onChange={(e) => {
                    setFilters({ ...filters, platform: e.target.value || undefined });
                    setPage(1);
                  }}
                  options={platformOptions}
                />
              </div>

              {/* Search */}
              <div>
                <label className="text-sm font-medium text-neutral-700 mb-1 block">
                  Search
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
                  <Input
                    placeholder="Search content..."
                    value={filters.search || ''}
                    onChange={(e) => {
                      setFilters({ ...filters, search: e.target.value || undefined });
                      setPage(1);
                    }}
                    className="pl-10"
                  />
                </div>
              </div>
            </div>

            {hasActiveFilters && (
              <div className="mt-4 flex items-center gap-2">
                <span className="text-sm text-neutral-500">Active filters:</span>
                {filters.sentiment && (
                  <Badge variant="secondary" className="gap-1">
                    Sentiment: {filters.sentiment}
                    <button
                      onClick={() => setFilters({ ...filters, sentiment: undefined })}
                      className="ml-1 hover:text-error-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {filters.platform && (
                  <Badge variant="secondary" className="gap-1">
                    Platform: {filters.platform}
                    <button
                      onClick={() => setFilters({ ...filters, platform: undefined })}
                      className="ml-1 hover:text-error-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {filters.search && (
                  <Badge variant="secondary" className="gap-1">
                    Search: "{filters.search}"
                    <button
                      onClick={() => setFilters({ ...filters, search: undefined })}
                      className="ml-1 hover:text-error-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  Clear all
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* No Project Selected Info */}
      {!filters.project_id && (
        <Alert variant="info">
          <BarChart3 className="h-4 w-4" />
          <span>
            Select a project from the filters to view and manage results, or{' '}
            <Link href="/dashboard/projects" className="font-medium underline">
              browse your projects
            </Link>
            .
          </span>
        </Alert>
      )}

      {/* Results Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40%]">Content</TableHead>
              <TableHead>Project</TableHead>
              <TableHead>Platform</TableHead>
              <TableHead>Sentiment</TableHead>
              <TableHead>Rating</TableHead>
              <TableHead>Date</TableHead>
              <TableHead className="w-[80px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableLoading colSpan={7} rows={10} />
            ) : !results?.items?.length ? (
              <TableEmpty
                colSpan={7}
                message={
                  filters.project_id
                    ? "No results found matching your filters."
                    : "Select a project to view results."
                }
              />
            ) : (
              results.items.map((result) => (
                <TableRow key={result.id}>
                  <TableCell className="max-w-md">
                    <div
                      className="cursor-pointer hover:text-primary-600"
                      onClick={() => setSelectedResult(result)}
                    >
                      {result.content.title && (
                        <div className="font-medium truncate">
                          {result.content.title}
                        </div>
                      )}
                      <div className="text-sm text-neutral-500 truncate">
                        {result.content.text?.slice(0, 100)}...
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Link
                      href={`/dashboard/projects/${result.project_id}`}
                      className="text-sm text-primary-600 hover:underline"
                    >
                      View Project
                    </Link>
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
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={() => setSelectedResult(result)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {result.source_url && (
                        <a
                          href={result.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex h-8 w-8 items-center justify-center rounded-md hover:bg-neutral-100"
                        >
                          <ExternalLink className="h-4 w-4 text-neutral-500" />
                        </a>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0 text-error-600"
                        onClick={() => setDeleteResultId(result.id)}
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

        {/* Pagination */}
        {results && results.pages > 1 && (
          <div className="flex items-center justify-between border-t border-neutral-200 px-4 py-3">
            <PaginationInfo
              currentPage={page}
              pageSize={20}
              totalItems={results.total}
            />
            <Pagination
              currentPage={page}
              totalPages={results.pages}
              onPageChange={setPage}
            />
          </div>
        )}
      </Card>

      {/* Result Detail Modal */}
      <Modal
        isOpen={!!selectedResult}
        onClose={() => setSelectedResult(null)}
        title="Result Details"
        size="lg"
      >
        {selectedResult && (
          <div className="space-y-4">
            {/* Content */}
            <div>
              <h4 className="text-sm font-medium text-neutral-500 mb-1">Content</h4>
              {selectedResult.content.title && (
                <p className="font-semibold text-neutral-900 mb-2">
                  {selectedResult.content.title}
                </p>
              )}
              <p className="text-neutral-700 whitespace-pre-wrap">
                {selectedResult.content.text}
              </p>
            </div>

            {/* Metadata */}
            <div className="grid gap-4 sm:grid-cols-2 border-t pt-4">
              <div>
                <h4 className="text-sm font-medium text-neutral-500 mb-1">Platform</h4>
                <Badge>{selectedResult.platform}</Badge>
              </div>
              <div>
                <h4 className="text-sm font-medium text-neutral-500 mb-1">Sentiment</h4>
                <SentimentBadge
                  sentiment={selectedResult.analysis.sentiment.label as any}
                  score={selectedResult.analysis.sentiment.confidence}
                />
              </div>
              {selectedResult.content.rating && (
                <div>
                  <h4 className="text-sm font-medium text-neutral-500 mb-1">Rating</h4>
                  <p className="font-medium">{selectedResult.content.rating}/5</p>
                </div>
              )}
              {selectedResult.content.author && (
                <div>
                  <h4 className="text-sm font-medium text-neutral-500 mb-1">Author</h4>
                  <p className="font-medium">{selectedResult.content.author}</p>
                </div>
              )}
              {selectedResult.content.date && (
                <div>
                  <h4 className="text-sm font-medium text-neutral-500 mb-1">Date</h4>
                  <p className="font-medium">{formatDate(selectedResult.content.date)}</p>
                </div>
              )}
              <div>
                <h4 className="text-sm font-medium text-neutral-500 mb-1">Scraped At</h4>
                <p className="font-medium">{formatRelativeTime(selectedResult.scraped_at)}</p>
              </div>
            </div>

            {/* Emotions */}
            {selectedResult.analysis.emotions && (
              <div className="border-t pt-4">
                <h4 className="text-sm font-medium text-neutral-500 mb-2">Emotions Detected</h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(selectedResult.analysis.emotions).map(([emotion, score]) => (
                    <Badge key={emotion} variant="secondary">
                      {emotion}: {Math.round((score as number) * 100)}%
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Keywords */}
            {selectedResult.analysis.keywords?.length > 0 && (
              <div className="border-t pt-4">
                <h4 className="text-sm font-medium text-neutral-500 mb-2">Keywords</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedResult.analysis.keywords.map((keyword: string) => (
                    <Badge key={keyword} variant="neutral">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Source URL */}
            {selectedResult.source_url && (
              <div className="border-t pt-4">
                <h4 className="text-sm font-medium text-neutral-500 mb-1">Source</h4>
                <a
                  href={selectedResult.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline flex items-center gap-1"
                >
                  {selectedResult.source_url}
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
            )}
          </div>
        )}
        <ModalFooter>
          <Button variant="outline" onClick={() => setSelectedResult(null)}>
            Close
          </Button>
          {selectedResult?.source_url && (
            <a
              href={selectedResult.source_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button>
                <ExternalLink className="mr-2 h-4 w-4" />
                View Source
              </Button>
            </a>
          )}
        </ModalFooter>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmModal
        isOpen={!!deleteResultId}
        onClose={() => setDeleteResultId(null)}
        onConfirm={handleDeleteResult}
        title="Delete Result"
        message="Are you sure you want to delete this result? This action cannot be undone."
        confirmText="Delete"
        variant="danger"
        isLoading={deleteResult.isPending}
      />
    </div>
  );
}
