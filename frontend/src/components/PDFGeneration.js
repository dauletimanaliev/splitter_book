import React, { useState } from 'react';
import { Download, FileText, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import styled from 'styled-components';

const GenerationContainer = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
`;

const GenerationHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 20px;
`;

const SectionList = styled.div`
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: white;
`;

const SectionItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
`;

const SectionInfo = styled.div`
  flex: 1;
`;

const SectionName = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
`;

const SectionDetails = styled.div`
  color: #666;
  font-size: 0.9rem;
`;

const DownloadButton = styled.button`
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.2s ease;

  &:hover {
    background: #1e7e34;
  }

  &:disabled {
    background: #6c757d;
    cursor: not-allowed;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
`;

const Spinner = styled.div`
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin: 15px 0;
`;

const ProgressFill = styled.div`
  height: 100%;
  background-color: #007bff;
  transition: width 0.3s ease;
  width: ${props => props.progress}%;
`;

const SuccessMessage = styled.div`
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
`;

// Удален неиспользуемый styled компонент

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
`;

const StatCard = styled.div`
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 5px;
`;

const StatLabel = styled.div`
  color: #666;
  font-size: 0.9rem;
`;

function PDFGeneration({ structure, selectedDesign, onGenerate, generatedFiles, loading }) {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');

  const handleGenerate = async () => {
    setProgress(0);
    setCurrentStep('Подготовка к генерации...');
    
    // Симулируем прогресс
    const steps = [
      'Анализ структуры...',
      'Применение дизайна...',
      'Создание PDF файлов...',
      'Финальная обработка...'
    ];
    
    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(steps[i]);
      setProgress((i + 1) * 25);
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    try {
      await onGenerate();
      setProgress(100);
      setCurrentStep('Генерация завершена!');
    } catch (error) {
      setCurrentStep('Ошибка при генерации');
    }
  };

  const downloadFile = async (bookId, filename) => {
    try {
      const response = await fetch(`/api/download/${bookId}/${filename}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Ошибка при скачивании файла');
      }
    } catch (error) {
      console.error('Ошибка скачивания:', error);
      alert('Ошибка при скачивании файла');
    }
  };

  if (loading) {
    return (
      <LoadingSpinner>
        <Spinner />
        <div style={{ marginLeft: '15px' }}>
          <div>{currentStep}</div>
          <ProgressBar>
            <ProgressFill progress={progress} />
          </ProgressBar>
        </div>
      </LoadingSpinner>
    );
  }

  if (generatedFiles) {
    return (
      <div>
        <SuccessMessage>
          <CheckCircle size={24} style={{ marginRight: '15px' }} />
          <div>
            <strong>Генерация завершена успешно!</strong>
            <div style={{ marginTop: '5px' }}>
              Создано {generatedFiles.total_sections} PDF файлов с дизайном "{selectedDesign}"
            </div>
          </div>
        </SuccessMessage>

        <StatsGrid>
          <StatCard>
            <StatValue>{generatedFiles.total_sections}</StatValue>
            <StatLabel>Создано разделов</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue>{selectedDesign}</StatValue>
            <StatLabel>Использованный дизайн</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue>{structure.total_pages}</StatValue>
            <StatLabel>Всего страниц</StatLabel>
          </StatCard>
        </StatsGrid>

        <SectionList>
          {generatedFiles.parts.map((file, index) => (
            <SectionItem key={index}>
              <SectionInfo>
                <SectionName>{file.title}</SectionName>
                <SectionDetails>
                  Страницы {file.start_page}-{file.end_page} • {file.pages_count} страниц
                </SectionDetails>
              </SectionInfo>
              <DownloadButton
                onClick={() => downloadFile(generatedFiles.book_id, file.filename)}
              >
                <Download size={16} style={{ marginRight: '8px' }} />
                Скачать
              </DownloadButton>
            </SectionItem>
          ))}
        </SectionList>

        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <button
            className="btn btn-success"
            onClick={() => {
              // Скачиваем все файлы
              generatedFiles.parts.forEach(file => {
                downloadFile(generatedFiles.book_id, file.filename);
              });
            }}
          >
            <Download size={16} style={{ marginRight: '8px' }} />
            Скачать все файлы
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <GenerationContainer>
        <GenerationHeader>
          <FileText size={24} style={{ marginRight: '15px', color: '#007bff' }} />
          <div>
            <h3 style={{ margin: 0, color: '#333' }}>Генерация PDF файлов</h3>
            <p style={{ margin: '5px 0 0 0', color: '#666' }}>
              Создание {structure.sections.length} PDF файлов с дизайном "{selectedDesign}"
            </p>
          </div>
        </GenerationHeader>

        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ marginBottom: '10px', color: '#333' }}>Будут созданы следующие разделы:</h4>
          <SectionList>
            {structure.sections.map((section, index) => (
              <SectionItem key={index}>
                <SectionInfo>
                  <SectionName>{section.name}</SectionName>
                  <SectionDetails>
                    Страницы {section.start_page}-{section.end_page} • 
                    {section.end_page - section.start_page + 1} страниц
                  </SectionDetails>
                </SectionInfo>
                <div style={{ color: '#28a745', fontSize: '0.9rem' }}>
                  ✓ Готов к генерации
                </div>
              </SectionItem>
            ))}
          </SectionList>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleGenerate}
          disabled={loading}
          style={{ width: '100%', padding: '15px', fontSize: '1.1rem' }}
        >
          {loading ? (
            <>
              <Loader size={20} style={{ marginRight: '10px' }} />
              Генерация...
            </>
          ) : (
            <>
              <FileText size={20} style={{ marginRight: '10px' }} />
              Начать генерацию PDF
            </>
          )}
        </button>
      </GenerationContainer>

      <div style={{ padding: '15px', background: '#e8f4fd', borderRadius: '6px' }}>
        <h4 style={{ marginBottom: '10px', color: '#004085' }}>
          <AlertCircle size={18} style={{ marginRight: '8px' }} />
          Что происходит при генерации:
        </h4>
        <ul style={{ color: '#004085', lineHeight: '1.6' }}>
          <li>Каждый раздел сохраняется как отдельный PDF файл</li>
          <li>Применяется выбранный дизайн (шрифты, цвета, отступы)</li>
          <li>Сохраняется оригинальный текст без изменений</li>
          <li>Добавляются номера страниц и оформление</li>
          <li>Файлы готовы для скачивания</li>
        </ul>
      </div>
    </div>
  );
}

export default PDFGeneration;
