/**
 * 文件上传服务（前端版）
 * 功能：文件验证、分类、Base64转换、预览生成
 */

export type FileCategory = 'image' | 'video' | 'audio' | 'document' | 'other';

export interface FileMetadata {
  filename: string;
  originalFilename: string;
  size: number;
  type: string;
  category: FileCategory;
  uploadTime: Date;
  previewUrl?: string;
  base64?: string;
}

export interface FileValidationResult {
  valid: boolean;
  error?: string;
}

class FileUploadService {
  // 允许的文件扩展名
  private readonly ALLOWED_EXTENSIONS = {
    image: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'],
    video: ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
    audio: ['mp3', 'wav', 'ogg', 'aac', 'm4a'],
    document: ['pdf', 'doc', 'docx', 'txt', 'md']
  };

  // 文件大小限制（字节）
  private readonly MAX_SIZES = {
    image: parseInt(process.env.MAX_IMAGE_SIZE || '10485760'), // 10MB
    video: parseInt(process.env.MAX_VIDEO_SIZE || '52428800'), // 50MB
    audio: 20971520, // 20MB
    document: 10485760 // 10MB
  };

  /**
   * 获取文件扩展名
   */
  private getFileExtension(filename: string): string {
    return filename.split('.').pop()?.toLowerCase() || '';
  }

  /**
   * 检测文件分类
   */
  categorizeFile(file: File): FileCategory {
    const extension = this.getFileExtension(file.name);
    
    for (const [category, extensions] of Object.entries(this.ALLOWED_EXTENSIONS)) {
      if (extensions.includes(extension)) {
        return category as FileCategory;
      }
    }
    
    return 'other';
  }

  /**
   * 验证文件
   */
  validateFile(file: File): FileValidationResult {
    const category = this.categorizeFile(file);
    
    // 检查是否支持的类型
    if (category === 'other') {
      const extension = this.getFileExtension(file.name);
      const allExtensions = Object.values(this.ALLOWED_EXTENSIONS).flat();
      return {
        valid: false,
        error: `不支持的文件类型: .${extension}。支持的类型: ${allExtensions.join(', ')}`
      };
    }
    
    // 检查文件大小
    const maxSize = this.MAX_SIZES[category];
    if (file.size > maxSize) {
      const sizeMB = (file.size / 1024 / 1024).toFixed(2);
      const maxSizeMB = (maxSize / 1024 / 1024).toFixed(0);
      return {
        valid: false,
        error: `文件大小超过限制: ${sizeMB}MB > ${maxSizeMB}MB`
      };
    }
    
    return { valid: true };
  }

  /**
   * 将文件转换为 Base64
   */
  async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        // 移除 data:image/jpeg;base64, 前缀
        const base64Data = base64.split(',')[1];
        resolve(base64Data);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  /**
   * 生成文件预览 URL
   */
  getFilePreview(file: File): string {
    return URL.createObjectURL(file);
  }

  /**
   * 处理文件上传（完整流程）
   */
  async processFile(file: File): Promise<FileMetadata> {
    // 1. 验证文件
    const validation = this.validateFile(file);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    // 2. 分类文件
    const category = this.categorizeFile(file);

    // 3. 转换 Base64
    const base64 = await this.fileToBase64(file);

    // 4. 生成预览
    const previewUrl = this.getFilePreview(file);

    // 5. 生成元数据
    const metadata: FileMetadata = {
      filename: `${Date.now()}_${file.name}`,
      originalFilename: file.name,
      size: file.size,
      type: file.type,
      category,
      uploadTime: new Date(),
      previewUrl,
      base64
    };

    return metadata;
  }

  /**
   * 格式化文件大小
   */
  formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  }
}

// 导出单例
export const fileUploadService = new FileUploadService();
