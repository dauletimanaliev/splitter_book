import React, { useState } from 'react';
import { FileText, Search, CheckCircle, AlertCircle } from 'lucide-react';
import styled from 'styled-components';

const BookInfo = styled.div`
  background: #e8f4fd;
  border: 1px solid #b8daff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
`;

const BookTitle = styled.h3`
  color: #004085;
  margin-bottom: 10px;
`;

const BookDetails = styled.div`
  color: #004085;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
`;

const DetailItem = styled.div`
  display: flex;
  align-items: center;
`;

const AnalysisOptions = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
`;

const OptionGroup = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
`;

const OptionCard = styled.div`
  border: 2px solid ${props => props.selected ? '#007bff' : '#e9ecef'};
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: ${props => props.selected ? '#f8f9ff' : 'white'};

  &:hover {
    border-color: #007bff;
    background: #f8f9ff;
  }
`;

const OptionTitle = styled.h4`
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
`;

const OptionDescription = styled.p`
  color: #666;
  font-size: 0.9rem;
  margin: 0;
`;

const PreviewSection = styled.div`
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
`;

const SectionList = styled.div`
  max-height: 300px;
  overflow-y: auto;
`;

const SectionItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
`;

const SectionName = styled.div`
  font-weight: 500;
  color: #333;
`;

const SectionPages = styled.div`
  color: #666;
  font-size: 0.9rem;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const Spinner = styled.div`
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

function StructureAnalysis({ bookData, onAnalyze, loading }) {
  const [selectedMode, setSelectedMode] = useState('by_headings');
  const [analysisResult, setAnalysisResult] = useState(null);

  const analysisModes = [
    {
      id: 'ai_analysis',
      title: 'AI Анализ',
      description: 'Использование искусственного интеллекта для точного определения структуры',
      icon: CheckCircle
    },
    {
      id: 'by_headings',
      title: 'По заголовкам',
      description: 'Автоматический поиск заголовков (Кіріспе, 1., 2., Қорытынды)',
      icon: Search
    },
    {
      id: 'by_meaning',
      title: 'По смыслу',
      description: 'Разделение на равные части по количеству страниц',
      icon: FileText
    },
    {
      id: 'auto',
      title: 'Автоматический',
      description: 'Сначала AI анализ, потом по заголовкам, если не найдены - по смыслу',
      icon: CheckCircle
    }
  ];

  const handleAnalyze = async () => {
    try {
      const result = await onAnalyze(selectedMode);
      setAnalysisResult(result);
    } catch (error) {
      console.error('Ошибка анализа:', error);
    }
  };

  if (loading) {
    return (
      <LoadingSpinner>
        <Spinner />
        <span style={{ marginLeft: '15px' }}>Анализ структуры книги...</span>
      </LoadingSpinner>
    );
  }

  return (
    <div>
      <BookInfo>
        <BookTitle>
          <FileText size={20} style={{ marginRight: '10px' }} />
          {bookData.filename}
        </BookTitle>
        <BookDetails>
          <DetailItem>
            <strong>Страниц:</strong> {bookData.pages_count}
          </DetailItem>
          <DetailItem>
            <strong>ID книги:</strong> {bookData.book_id}
          </DetailItem>
        </BookDetails>
      </BookInfo>

      <AnalysisOptions>
        <h4 style={{ marginBottom: '15px', color: '#333' }}>Выберите метод анализа:</h4>
        <OptionGroup>
          {analysisModes.map((mode) => {
            const Icon = mode.icon;
            return (
              <OptionCard
                key={mode.id}
                selected={selectedMode === mode.id}
                onClick={() => setSelectedMode(mode.id)}
              >
                <OptionTitle>
                  <Icon size={18} style={{ marginRight: '8px' }} />
                  {mode.title}
                </OptionTitle>
                <OptionDescription>{mode.description}</OptionDescription>
              </OptionCard>
            );
          })}
        </OptionGroup>

        <button
          className="btn btn-primary"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? 'Анализ...' : 'Начать анализ'}
        </button>
      </AnalysisOptions>

      {analysisResult && (
        <PreviewSection>
          <h4 style={{ marginBottom: '15px', color: '#333' }}>
            <CheckCircle size={18} style={{ marginRight: '8px', color: '#28a745' }} />
            Найдено разделов: {analysisResult.sections_count}
          </h4>
          
          <SectionList>
            {analysisResult.structure.sections.map((section, index) => (
              <SectionItem key={index}>
                <SectionName>{section.name}</SectionName>
                <SectionPages>
                  Страницы {section.start_page}-{section.end_page}
                </SectionPages>
              </SectionItem>
            ))}
          </SectionList>

          <div style={{ marginTop: '15px', padding: '10px', background: '#d4edda', borderRadius: '6px' }}>
            <div style={{ color: '#155724', fontSize: '0.9rem' }}>
              <strong>Метод анализа:</strong> {analysisResult.structure.analysis_method}
            </div>
          </div>
        </PreviewSection>
      )}

      <div style={{ marginTop: '20px', padding: '15px', background: '#fff3cd', borderRadius: '6px' }}>
        <h4 style={{ marginBottom: '10px', color: '#856404' }}>
          <AlertCircle size={18} style={{ marginRight: '8px' }} />
          Информация об анализе:
        </h4>
        <ul style={{ color: '#856404', lineHeight: '1.6', margin: 0 }}>
          <li>Система автоматически найдет заголовки в тексте</li>
          <li>Если заголовки не найдены, книга будет разделена на равные части</li>
          <li>Каждый раздел будет сохранен как отдельный PDF файл</li>
          <li>Вы можете выбрать дизайн для оформления PDF</li>
        </ul>
      </div>
    </div>
  );
}

export default StructureAnalysis;
