/**
 * API 客户端工具
 * 统一处理 API 调用、错误处理和响应展示
 */

class APIClient {
    constructor(baseURL = 'http://localhost:7860') {
        this.baseURL = baseURL;
    }

    /**
     * 发送 POST 请求
     */
    async post(url, data) {
        const fullURL = `${this.baseURL}${url}`;
        const startTime = Date.now();

        try {
            const response = await fetch(fullURL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const duration = Date.now() - startTime;
            const result = await response.json();

            return {
                success: response.ok,
                status: response.status,
                data: result,
                duration,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            const duration = Date.now() - startTime;
            return {
                success: false,
                status: 0,
                error: error.message,
                duration,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * 发送 GET 请求
     */
    async get(url) {
        const fullURL = `${this.baseURL}${url}`;
        const startTime = Date.now();

        try {
            const response = await fetch(fullURL);
            const duration = Date.now() - startTime;
            const result = await response.json();

            return {
                success: response.ok,
                status: response.status,
                data: result,
                duration,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            const duration = Date.now() - startTime;
            return {
                success: false,
                status: 0,
                error: error.message,
                duration,
                timestamp: new Date().toISOString()
            };
        }
    }
}

// 导出全局实例
const apiClient = new APIClient();

/**
 * JSON 格式化显示
 */
function formatJSON(data) {
    return JSON.stringify(data, null, 2);
}

/**
 * 显示请求信息
 */
function displayRequest(containerId, url, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <div class="request-info">
            <div class="info-header">请求</div>
            <div class="info-item"><strong>URL:</strong> ${url}</div>
            <div class="info-item"><strong>时间:</strong> ${new Date().toLocaleString()}</div>
            <pre class="json-content">${formatJSON(data)}</pre>
        </div>
    `;
}

/**
 * 显示响应信息
 */
function displayResponse(containerId, response) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const statusClass = response.success ? 'status-success' : 'status-error';
    const statusText = response.success ? '成功' : '失败';

    container.innerHTML = `
        <div class="response-info">
            <div class="info-header ${statusClass}">响应 - ${statusText}</div>
            <div class="info-item"><strong>状态码:</strong> ${response.status}</div>
            <div class="info-item"><strong>耗时:</strong> ${response.duration}ms</div>
            <div class="info-item"><strong>时间:</strong> ${new Date(response.timestamp).toLocaleString()}</div>
            <pre class="json-content">${formatJSON(response.data || response.error)}</pre>
        </div>
    `;
}

/**
 * 清空显示区域
 */
function clearDisplay(requestId, responseId) {
    const requestContainer = document.getElementById(requestId);
    const responseContainer = document.getElementById(responseId);

    if (requestContainer) requestContainer.innerHTML = '';
    if (responseContainer) responseContainer.innerHTML = '';
}

/**
 * 显示加载状态
 */
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <div>请求中...</div>
        </div>
    `;
}

/**
 * 保存测试历史到 localStorage
 */
function saveTestHistory(serviceName, testData) {
    const key = `test_history_${serviceName}`;
    const history = JSON.parse(localStorage.getItem(key) || '[]');

    history.unshift({
        ...testData,
        timestamp: new Date().toISOString()
    });

    // 只保留最近 10 条
    if (history.length > 10) {
        history.pop();
    }

    localStorage.setItem(key, JSON.stringify(history));
}

/**
 * 获取测试历史
 */
function getTestHistory(serviceName) {
    const key = `test_history_${serviceName}`;
    return JSON.parse(localStorage.getItem(key) || '[]');
}

/**
 * 清空测试历史
 */
function clearTestHistory(serviceName) {
    const key = `test_history_${serviceName}`;
    localStorage.removeItem(key);
}

/**
 * 复制到剪贴板
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('已复制到剪贴板');
    } catch (err) {
        showToast('复制失败: ' + err.message, 'error');
    }
}

/**
 * 显示提示消息
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 2000);
}

/**
 * 从表单获取数据
 */
function getFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return {};

    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        // 尝试解析 JSON 字符串
        try {
            data[key] = JSON.parse(value);
        } catch {
            data[key] = value;
        }
    }

    return data;
}

/**
 * 填充表单数据
 */
function fillFormData(formId, data) {
    const form = document.getElementById(formId);
    if (!form) return;

    for (let key in data) {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            if (typeof data[key] === 'object') {
                input.value = JSON.stringify(data[key], null, 2);
            } else {
                input.value = data[key];
            }
        }
    }
}
