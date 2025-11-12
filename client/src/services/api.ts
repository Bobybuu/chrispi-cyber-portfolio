// client/src/services/api.ts
const API_BASE_URL = 'http://localhost:8000/api/contact';

interface ContactFormData {
  name: string;
  email: string;
  phone?: string;
  company?: string;
  subject?: string;
  message: string;
  category?: string;
  consent_given: boolean;
  newsletter_subscribed?: boolean;
}

interface ContactConfig {
  is_enabled: boolean;
  required_fields: {
    name: boolean;
    email: boolean;
    phone: boolean;
    company: boolean;
    subject: boolean;
  };
  categories: string[];
  recaptcha_enabled: boolean;
  recaptcha_site_key: string;
}

interface ApiResponse<T> {
  status: string;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

class ApiError extends Error {
  code: string;
  details?: any;

  constructor(code: string, message: string, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
  }
}

export const contactAPI = {
  async getConfig(): Promise<ContactConfig> {
    const response = await fetch(`${API_BASE_URL}/config/`);
    const result: ApiResponse<ContactConfig> = await response.json();
    
    if (result.status === 'success' && result.data) {
      return result.data;
    } else {
      throw new ApiError(
        result.error?.code || 'UNKNOWN_ERROR',
        result.error?.message || 'Failed to fetch contact configuration'
      );
    }
  },

  async sendMessage(formData: ContactFormData): Promise<{ id: string }> {
    const response = await fetch(`${API_BASE_URL}/messages/create/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    const result: ApiResponse<{ id: string }> = await response.json();

    if (result.status === 'success' && result.data) {
      return result.data;
    } else {
      throw new ApiError(
        result.error?.code || 'UNKNOWN_ERROR',
        result.error?.message || 'Failed to send message',
        result.error?.details
      );
    }
  },
};