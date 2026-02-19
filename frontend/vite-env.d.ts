/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_DASHSCOPE_API_KEY: string
  readonly VITE_DASHSCOPE_BASE_URL: string
  readonly VITE_DASHSCOPE_MODEL: string
  readonly VITE_MAX_IMAGE_SIZE: string
  readonly VITE_MAX_VIDEO_SIZE: string
  readonly VITE_ALIYUN_NLS_APPKEY: string
  readonly VITE_ALIYUN_NLS_TOKEN: string
  readonly VITE_IMAGE_GEN_MODEL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
