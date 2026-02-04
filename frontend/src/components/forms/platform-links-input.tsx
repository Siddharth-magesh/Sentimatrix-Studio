'use client';

import { useState } from 'react';
import {
  Button,
  Card,
  CardContent,
  Input,
  Label,
  Alert,
} from '@/components/ui';
import {
  ShoppingBag,
  Gamepad2,
  Youtube,
  MessageSquare,
  Search,
  Star,
  MapPin,
  Plus,
  X,
  ChevronDown,
  ChevronUp,
  ExternalLink,
} from 'lucide-react';
import type { PlatformLinks, PlatformLink } from '@/lib/api';

interface PlatformConfig {
  id: keyof PlatformLinks;
  name: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  description: string;
  urlPattern: string;
  urlExample: string;
  supportsCountry?: boolean;
  supportsLanguage?: boolean;
  countries?: { value: string; label: string }[];
}

const PLATFORMS: PlatformConfig[] = [
  {
    id: 'amazon',
    name: 'Amazon',
    icon: ShoppingBag,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 hover:bg-orange-100',
    description: 'Product reviews from Amazon marketplace',
    urlPattern: 'amazon.com/dp/ASIN or amazon.com/product-reviews/ASIN',
    urlExample: 'https://www.amazon.com/dp/B09V3KXJPB',
    supportsCountry: true,
    countries: [
      { value: 'us', label: 'United States' },
      { value: 'uk', label: 'United Kingdom' },
      { value: 'de', label: 'Germany' },
      { value: 'fr', label: 'France' },
      { value: 'es', label: 'Spain' },
      { value: 'it', label: 'Italy' },
      { value: 'jp', label: 'Japan' },
      { value: 'ca', label: 'Canada' },
      { value: 'in', label: 'India' },
      { value: 'au', label: 'Australia' },
    ],
  },
  {
    id: 'steam',
    name: 'Steam',
    icon: Gamepad2,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 hover:bg-blue-100',
    description: 'Game reviews from Steam store',
    urlPattern: 'store.steampowered.com/app/APP_ID',
    urlExample: 'https://store.steampowered.com/app/730',
    supportsLanguage: true,
  },
  {
    id: 'youtube',
    name: 'YouTube',
    icon: Youtube,
    color: 'text-red-600',
    bgColor: 'bg-red-50 hover:bg-red-100',
    description: 'Comments from YouTube videos',
    urlPattern: 'youtube.com/watch?v=VIDEO_ID',
    urlExample: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
  },
  {
    id: 'reddit',
    name: 'Reddit',
    icon: MessageSquare,
    color: 'text-orange-500',
    bgColor: 'bg-orange-50 hover:bg-orange-100',
    description: 'Comments from Reddit posts',
    urlPattern: 'reddit.com/r/subreddit/comments/POST_ID',
    urlExample: 'https://www.reddit.com/r/technology/comments/abc123',
  },
  {
    id: 'google',
    name: 'Google Reviews',
    icon: Search,
    color: 'text-green-600',
    bgColor: 'bg-green-50 hover:bg-green-100',
    description: 'Business reviews from Google Maps',
    urlPattern: 'google.com/maps/place/PLACE_ID',
    urlExample: 'https://www.google.com/maps/place/...',
  },
  {
    id: 'trustpilot',
    name: 'Trustpilot',
    icon: Star,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-50 hover:bg-emerald-100',
    description: 'Company reviews from Trustpilot',
    urlPattern: 'trustpilot.com/review/DOMAIN',
    urlExample: 'https://www.trustpilot.com/review/example.com',
  },
  {
    id: 'yelp',
    name: 'Yelp',
    icon: MapPin,
    color: 'text-red-500',
    bgColor: 'bg-red-50 hover:bg-red-100',
    description: 'Business reviews from Yelp',
    urlPattern: 'yelp.com/biz/BUSINESS_NAME',
    urlExample: 'https://www.yelp.com/biz/restaurant-name-city',
  },
];

interface PlatformLinksInputProps {
  value: PlatformLinks;
  onChange: (value: PlatformLinks) => void;
  selectedPlatforms: string[];
  onPlatformToggle: (platformId: string) => void;
}

export function PlatformLinksInput({
  value,
  onChange,
  selectedPlatforms,
  onPlatformToggle,
}: PlatformLinksInputProps) {
  const [expandedPlatforms, setExpandedPlatforms] = useState<string[]>([]);

  const toggleExpanded = (platformId: string) => {
    setExpandedPlatforms((prev) =>
      prev.includes(platformId)
        ? prev.filter((id) => id !== platformId)
        : [...prev, platformId]
    );
  };

  const addLink = (platformId: keyof PlatformLinks) => {
    const newLink: PlatformLink = { url: '' };
    onChange({
      ...value,
      [platformId]: [...(value[platformId] || []), newLink],
    });
  };

  const updateLink = (
    platformId: keyof PlatformLinks,
    index: number,
    updates: Partial<PlatformLink>
  ) => {
    const links = [...(value[platformId] || [])];
    links[index] = { ...links[index], ...updates };
    onChange({ ...value, [platformId]: links });
  };

  const removeLink = (platformId: keyof PlatformLinks, index: number) => {
    const links = [...(value[platformId] || [])];
    links.splice(index, 1);
    onChange({ ...value, [platformId]: links });
  };

  const getPlatformLinkCount = (platformId: keyof PlatformLinks): number => {
    return (value[platformId] || []).filter((l) => l.url.trim()).length;
  };

  const getTotalLinkCount = (): number => {
    return PLATFORMS.reduce((sum, p) => sum + getPlatformLinkCount(p.id), 0);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Label className="text-base font-medium">Data Sources</Label>
        <span className="text-sm text-neutral-500">
          {getTotalLinkCount()} link{getTotalLinkCount() !== 1 ? 's' : ''} configured
        </span>
      </div>

      <Alert variant="info">
        Select the platforms you want to scrape and add the specific URLs for your product/brand.
      </Alert>

      <div className="grid gap-3">
        {PLATFORMS.map((platform) => {
          const Icon = platform.icon;
          const isSelected = selectedPlatforms.includes(platform.id);
          const isExpanded = expandedPlatforms.includes(platform.id);
          const links = value[platform.id] || [];
          const linkCount = getPlatformLinkCount(platform.id);

          return (
            <Card
              key={platform.id}
              className={`transition-all ${
                isSelected ? 'ring-2 ring-primary-500 ring-offset-1' : ''
              }`}
            >
              <div
                className={`flex items-center justify-between p-4 cursor-pointer ${platform.bgColor} rounded-t-lg`}
                onClick={() => {
                  if (!isSelected) {
                    onPlatformToggle(platform.id);
                    toggleExpanded(platform.id);
                  } else {
                    toggleExpanded(platform.id);
                  }
                }}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-lg bg-white shadow-sm`}
                  >
                    <Icon className={`h-5 w-5 ${platform.color}`} />
                  </div>
                  <div>
                    <h3 className="font-medium text-neutral-900">{platform.name}</h3>
                    <p className="text-sm text-neutral-500">{platform.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {isSelected && linkCount > 0 && (
                    <span className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">
                      {linkCount} link{linkCount !== 1 ? 's' : ''}
                    </span>
                  )}
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onPlatformToggle(platform.id);
                      if (!isSelected) {
                        setExpandedPlatforms((prev) => [...prev, platform.id]);
                      }
                    }}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                      isSelected
                        ? 'bg-primary-600 text-white hover:bg-primary-700'
                        : 'bg-white text-neutral-700 hover:bg-neutral-50 border'
                    }`}
                  >
                    {isSelected ? 'Selected' : 'Select'}
                  </button>
                  {isSelected && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleExpanded(platform.id);
                      }}
                      className="p-1 rounded hover:bg-white/50"
                    >
                      {isExpanded ? (
                        <ChevronUp className="h-5 w-5 text-neutral-500" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-neutral-500" />
                      )}
                    </button>
                  )}
                </div>
              </div>

              {isSelected && isExpanded && (
                <CardContent className="border-t p-4 space-y-4">
                  <div className="flex items-center gap-2 text-sm text-neutral-500">
                    <ExternalLink className="h-4 w-4" />
                    <span>URL format: {platform.urlPattern}</span>
                  </div>

                  <div className="space-y-3">
                    {links.map((link, index) => (
                      <div key={index} className="flex gap-2">
                        <div className="flex-1 space-y-2">
                          <Input
                            placeholder={platform.urlExample}
                            value={link.url}
                            onChange={(e) =>
                              updateLink(platform.id, index, { url: e.target.value })
                            }
                          />
                          <div className="flex gap-2">
                            <Input
                              placeholder="Label (optional)"
                              value={link.label || ''}
                              onChange={(e) =>
                                updateLink(platform.id, index, {
                                  label: e.target.value || undefined,
                                })
                              }
                              className="flex-1"
                            />
                            {platform.supportsCountry && (
                              <select
                                className="rounded-lg border border-neutral-300 px-3 py-2 text-sm"
                                value={link.country || ''}
                                onChange={(e) =>
                                  updateLink(platform.id, index, {
                                    country: e.target.value || undefined,
                                  })
                                }
                              >
                                <option value="">Country (auto)</option>
                                {platform.countries?.map((c) => (
                                  <option key={c.value} value={c.value}>
                                    {c.label}
                                  </option>
                                ))}
                              </select>
                            )}
                            {platform.supportsLanguage && (
                              <select
                                className="rounded-lg border border-neutral-300 px-3 py-2 text-sm"
                                value={link.language || ''}
                                onChange={(e) =>
                                  updateLink(platform.id, index, {
                                    language: e.target.value || undefined,
                                  })
                                }
                              >
                                <option value="">Language (all)</option>
                                <option value="en">English</option>
                                <option value="es">Spanish</option>
                                <option value="fr">French</option>
                                <option value="de">German</option>
                                <option value="zh">Chinese</option>
                                <option value="ja">Japanese</option>
                                <option value="ko">Korean</option>
                                <option value="ru">Russian</option>
                              </select>
                            )}
                          </div>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeLink(platform.id, index)}
                          className="text-neutral-400 hover:text-red-600"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>

                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => addLink(platform.id)}
                    className="w-full"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Add {platform.name} Link
                  </Button>
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}

export { PLATFORMS };
