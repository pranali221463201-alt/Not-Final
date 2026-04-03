import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Sparkles, Copy, Download } from 'lucide-react';

interface AdResult {
  headline: string;
  shortCaption: string;
  longCaption: string;
  cta: string;
  textForAd: string[];
  visualRecommendation: string;
  hashtags: string[];
  bestFormat: string;
}

export function AdvertisementGenerator() {
  const [showForm, setShowForm] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [adResult, setAdResult] = useState<AdResult | null>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    businessName: '',
    products: '',
    targetAudience: '',
    location: '',
    usp: '',
    offer: '',
    contact: '',
    platform: 'instagram',
    tone: 'modern',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedImage(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const generateAd = async () => {
    if (!formData.businessName || !formData.products) {
      alert('Please fill in business name and products');
      return;
    }

    setIsGenerating(true);

    try {
      const params = new URLSearchParams({
        business_name: formData.businessName,
        products: formData.products,
        target_audience: formData.targetAudience || '',
        location: formData.location || '',
        usp: formData.usp || '',
        offer: formData.offer || '',
        contact: formData.contact || '',
        platform: formData.platform,
        tone: formData.tone,
      });

      const response = await fetch(`http://localhost:8000/api/ads/generate?${params}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate advertisement');
      }

      const data = await response.json();
      
      if (data.success && data.data) {
        setAdResult(data.data);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error generating ad:', error);
      alert(`Error generating advertisement: ${error instanceof Error ? error.message : 'Please try again.'}`);
    }

    setIsGenerating(false);
  };



  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const downloadAd = () => {
    if (!adResult) return;

    const content = `
ADVERTISEMENT FOR: ${formData.businessName}
Generated on: ${new Date().toLocaleDateString()}

HEADLINE:
${adResult.headline}

SHORT CAPTION (Instagram/WhatsApp):
${adResult.shortCaption}

LONG CAPTION (Facebook/LinkedIn):
${adResult.longCaption}

CALL-TO-ACTION:
${adResult.cta}

TEXT FOR AD IMAGE/VIDEO:
${adResult.textForAd.join('\n')}

VISUAL RECOMMENDATIONS:
${adResult.visualRecommendation}

HASHTAGS:
${adResult.hashtags.join(' ')}

BEST FORMAT:
${adResult.bestFormat}

BUSINESS DETAILS:
Business: ${formData.businessName}
Products: ${formData.products}
Location: ${formData.location}
Contact: ${formData.contact}
Platform: ${formData.platform}
    `;

    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', `${formData.businessName}-ad.txt`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div>
      {!showForm && !adResult && (
        <Button onClick={() => setShowForm(true)} className="gap-2 w-full">
          <Sparkles className="w-4 h-4" />
          Generate Advertisement
        </Button>
      )}

      {showForm && !adResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              Advertisement Generator for Plastic Manufacturers
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label className="text-xs">Business Name *</Label>
                <Input
                  name="businessName"
                  placeholder="e.g., ABC Plastic Industries"
                  value={formData.businessName}
                  onChange={handleInputChange}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Products *</Label>
                <Input
                  name="products"
                  placeholder="e.g., Plastic containers, buckets, packaging"
                  value={formData.products}
                  onChange={handleInputChange}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Target Audience</Label>
                <Input
                  name="targetAudience"
                  placeholder="e.g., Retail customers, shop owners, wholesalers"
                  value={formData.targetAudience}
                  onChange={handleInputChange}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Location</Label>
                <Input
                  name="location"
                  placeholder="e.g., Virar, Maharashtra"
                  value={formData.location}
                  onChange={handleInputChange}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Unique Selling Points</Label>
                <Input
                  name="usp"
                  placeholder="e.g., Durable, affordable, custom colors, bulk available"
                  value={formData.usp}
                  onChange={handleInputChange}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Offer/Discount</Label>
                <Input
                  name="offer"
                  placeholder="e.g., 10% off on bulk orders (optional)"
                  value={formData.offer}
                  onChange={handleInputChange}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Contact Details</Label>
                <Input
                  name="contact"
                  placeholder="e.g., +91 9876543210 or email"
                  value={formData.contact}
                  onChange={handleInputChange}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Platform</Label>
                <Select value={formData.platform} onValueChange={(v) => handleSelectChange('platform', v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="instagram">Instagram</SelectItem>
                    <SelectItem value="facebook">Facebook</SelectItem>
                    <SelectItem value="linkedin">LinkedIn</SelectItem>
                    <SelectItem value="whatsapp">WhatsApp Business</SelectItem>
                    <SelectItem value="youtube">YouTube Shorts</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Tone</Label>
                <Select value={formData.tone} onValueChange={(v) => handleSelectChange('tone', v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="professional">Professional</SelectItem>
                    <SelectItem value="modern">Modern</SelectItem>
                    <SelectItem value="premium">Premium</SelectItem>
                    <SelectItem value="affordable">Affordable</SelectItem>
                    <SelectItem value="industrial">Industrial</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Image Upload */}
            <div className="space-y-1.5">
              <Label className="text-xs">Upload Product Image (Optional)</Label>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="block w-full text-sm border border-slate-200 rounded-md p-2"
              />
              {uploadedImage && (
                <div className="mt-2">
                  <img
                    src={uploadedImage}
                    alt="Uploaded"
                    className="max-w-xs h-32 object-cover rounded-md"
                  />
                </div>
              )}
            </div>

            <div className="flex gap-2 pt-4">
              <Button onClick={generateAd} disabled={isGenerating} className="flex-1">
                {isGenerating ? 'Generating...' : 'Generate Advertisement'}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowForm(false);
                  setAdResult(null);
                }}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {adResult && (
        <Card className="space-y-4">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Your Generated Advertisement</span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadAd}
                  className="gap-1"
                >
                  <Download className="w-4 h-4" />
                  Download
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setAdResult(null);
                    setShowForm(false);
                  }}
                >
                  New Ad
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Headline */}
            <div className="border-l-4 border-primary pl-4">
              <h3 className="font-bold text-lg mb-2">📍 Headline</h3>
              <p className="text-2xl font-bold text-primary mb-2">{adResult.headline}</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(adResult.headline)}
                className="gap-1"
              >
                <Copy className="w-3 h-3" />
                Copy
              </Button>
            </div>

            {/* Short Caption */}
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-bold mb-2">📱 Short Caption (Instagram/WhatsApp)</h3>
              <p className="text-sm mb-2">{adResult.shortCaption}</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(adResult.shortCaption)}
                className="gap-1"
              >
                <Copy className="w-3 h-3" />
                Copy
              </Button>
            </div>

            {/* Long Caption */}
            <div className="border-l-4 border-indigo-500 pl-4">
              <h3 className="font-bold mb-2">📘 Long Caption (Facebook/LinkedIn)</h3>
              <p className="text-sm mb-2 whitespace-pre-wrap">{adResult.longCaption}</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(adResult.longCaption)}
                className="gap-1"
              >
                <Copy className="w-3 h-3" />
                Copy
              </Button>
            </div>

            {/* CTA */}
            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="font-bold mb-2">🎯 Call-to-Action</h3>
              <p className="text-lg font-semibold text-green-600 mb-2">{adResult.cta}</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(adResult.cta)}
                className="gap-1"
              >
                <Copy className="w-3 h-3" />
                Copy
              </Button>
            </div>

            {/* Text for Ad */}
            <div className="border-l-4 border-yellow-500 pl-4">
              <h3 className="font-bold mb-2">✍️ Text for Ad Image/Video</h3>
              <div className="space-y-2">
                {adResult.textForAd.map((text, idx) => (
                  <div key={idx} className="bg-yellow-50 p-2 rounded text-sm">
                    • {text}
                  </div>
                ))}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(adResult.textForAd.join('\n'))}
                className="gap-1 mt-2"
              >
                <Copy className="w-3 h-3" />
                Copy All
              </Button>
            </div>

            {/* Visual Recommendations */}
            <div className="border-l-4 border-purple-500 pl-4 bg-purple-50 p-3 rounded">
              <h3 className="font-bold mb-2">🎨 Visual Recommendations</h3>
              <p className="text-sm whitespace-pre-wrap">{adResult.visualRecommendation}</p>
            </div>

            {/* Hashtags */}
            <div className="border-l-4 border-pink-500 pl-4">
              <h3 className="font-bold mb-2">#️⃣ Hashtags</h3>
              <div className="flex flex-wrap gap-2 mb-2">
                {adResult.hashtags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    {tag}
                  </Badge>
                ))}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(adResult.hashtags.join(' '))}
                className="gap-1"
              >
                <Copy className="w-3 h-3" />
                Copy All Hashtags
              </Button>
            </div>

            {/* Best Format */}
            <div className="border-l-4 border-cyan-500 pl-4 bg-cyan-50 p-3 rounded">
              <h3 className="font-bold mb-2">📺 Best Format for This Platform</h3>
              <p className="text-sm font-semibold">{adResult.bestFormat}</p>
            </div>

            {/* Image Display */}
            {uploadedImage && (
              <div className="border-l-4 border-orange-500 pl-4">
                <h3 className="font-bold mb-2">🖼️ Your Uploaded Image</h3>
                <img
                  src={uploadedImage}
                  alt="Product"
                  className="max-w-sm h-48 object-cover rounded-md"
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Use this image with the text overlay suggestions provided above for maximum impact.
                </p>
              </div>
            )}

            <div className="bg-blue-50 p-4 rounded border border-blue-200 text-sm space-y-2">
              <h4 className="font-bold">💡 Tips for Best Results:</h4>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Use bright, eye-catching colors that match your brand</li>
                <li>Include product photos or factory images for trust building</li>
                <li>Add customer testimonials or before-after comparisons</li>
                <li>Post consistently on your chosen platform for better reach</li>
                <li>Use the recommended hashtags to maximize visibility</li>
                <li>Update your ad after 2 weeks if performance is low</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
