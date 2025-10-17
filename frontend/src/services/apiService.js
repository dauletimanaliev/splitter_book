import axios from 'axios';

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 300000, // 5 минут для больших файлов
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Сервер ответил с кодом ошибки
      const message = error.response.data?.detail || error.response.data?.message || 'Произошла ошибка сервера';
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // Запрос был отправлен, но ответа не получено
      return Promise.reject(new Error('Сервер не отвечает. Проверьте подключение к интернету.'));
    } else {
      // Что-то пошло не так при настройке запроса
      return Promise.reject(new Error('Ошибка при отправке запроса'));
    }
  }
);

class ApiService {
  /**
   * Загрузка книги
   * @param {FormData} formData - Данные файла
   * @returns {Promise} - Ответ сервера
   */
  async uploadBook(formData) {
    try {
      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload Progress: ${percentCompleted}%`);
        },
      });
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Анализ структуры книги
   * @param {string} bookId - ID книги
   * @param {string} splitMode - Режим разделения
   * @returns {Promise} - Ответ сервера
   */
  async analyzeStructure(bookId, splitMode = 'by_headings') {
    try {
      const response = await api.post('/analyze', {
        book_id: bookId,
        split_mode: splitMode,
      });
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Генерация PDF файлов
   * @param {string} bookId - ID книги
   * @param {string} design - Название дизайна
   * @returns {Promise} - Ответ сервера
   */
  async generatePDFs(bookId, design = 'classic_islamic') {
    try {
      const response = await api.post('/generate', {
        book_id: bookId,
        design: design,
      });
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Получение списка доступных дизайнов
   * @returns {Promise} - Ответ сервера
   */
  async getAvailableDesigns() {
    try {
      const response = await api.get('/designs');
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Скачивание PDF файла
   * @param {string} bookId - ID книги
   * @param {string} filename - Имя файла
   * @returns {Promise} - Blob файла
   */
  async downloadPDF(bookId, filename) {
    try {
      const response = await api.get(`/download/${bookId}/${filename}`, {
        responseType: 'blob',
      });
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Получение статуса генерации
   * @param {string} bookId - ID книги
   * @returns {Promise} - Ответ сервера
   */
  async getGenerationStatus(bookId) {
    try {
      const response = await api.get(`/status/${bookId}`);
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Получение списка всех генераций
   * @returns {Promise} - Ответ сервера
   */
  async getAllGenerations() {
    try {
      const response = await api.get('/generations');
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Удаление генерации
   * @param {string} bookId - ID книги
   * @returns {Promise} - Ответ сервера
   */
  async deleteGeneration(bookId) {
    try {
      const response = await api.delete(`/generations/${bookId}`);
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Получение информации о книге
   * @param {string} bookId - ID книги
   * @returns {Promise} - Ответ сервера
   */
  async getBookInfo(bookId) {
    try {
      const response = await api.get(`/books/${bookId}`);
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Получение структуры книги
   * @param {string} bookId - ID книги
   * @returns {Promise} - Ответ сервера
   */
  async getBookStructure(bookId) {
    try {
      const response = await api.get(`/books/${bookId}/structure`);
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Создание пользовательского разделения
   * @param {string} bookId - ID книги
   * @param {Array} customSections - Пользовательские разделы
   * @param {string} design - Дизайн
   * @returns {Promise} - Ответ сервера
   */
  async createCustomSplit(bookId, customSections, design = 'classic_islamic') {
    try {
      const response = await api.post('/custom-split', {
        book_id: bookId,
        sections: customSections,
        design: design,
      });
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Получение превью раздела
   * @param {string} bookId - ID книги
   * @param {Object} section - Данные раздела
   * @returns {Promise} - Ответ сервера
   */
  async getSectionPreview(bookId, section) {
    try {
      const response = await api.post('/preview', {
        book_id: bookId,
        section: section,
      });
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Проверка здоровья API
   * @returns {Promise} - Ответ сервера
   */
  async healthCheck() {
    try {
      const response = await api.get('/');
      return response;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Установка базового URL
   * @param {string} baseURL - Базовый URL
   */
  setBaseURL(baseURL) {
    api.defaults.baseURL = baseURL;
  }

  /**
   * Установка таймаута
   * @param {number} timeout - Таймаут в миллисекундах
   */
  setTimeout(timeout) {
    api.defaults.timeout = timeout;
  }
}

// Создаем и экспортируем экземпляр сервиса
export const apiService = new ApiService();

// Экспортируем также экземпляр axios для прямого использования
export { api };

export default apiService;
