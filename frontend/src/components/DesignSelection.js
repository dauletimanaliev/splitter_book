import React, { useState, useEffect } from 'react';
import { Palette, Check, Star } from 'lucide-react';
import styled from 'styled-components';
import { apiService } from '../services/apiService';

const DesignGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
`;

const DesignCard = styled.div`
  border: 3px solid ${props => props.selected ? '#007bff' : '#e9ecef'};
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => props.selected ? '#f8f9ff' : 'white'};
  position: relative;

  &:hover {
    border-color: #007bff;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
`;

const DesignPreview = styled.div`
  height: 200px;
  border-radius: 8px;
  margin-bottom: 15px;
  background: ${props => props.$background};
  border: 1px solid #ddd;
  position: relative;
  overflow: hidden;
`;

const PreviewContent = styled.div`
  padding: 15px;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const PreviewTitle = styled.div`
  font-family: ${props => props.fontFamily};
  font-size: ${props => props.fontSize}px;
  color: ${props => props.color};
  font-weight: bold;
  margin-bottom: 10px;
  text-align: center;
`;

const PreviewHeading = styled.div`
  font-family: ${props => props.fontFamily};
  font-size: ${props => props.fontSize}px;
  color: ${props => props.color};
  font-weight: bold;
  margin-bottom: 8px;
`;

const PreviewText = styled.div`
  font-family: ${props => props.fontFamily};
  font-size: ${props => props.fontSize}px;
  color: ${props => props.color};
  line-height: 1.4;
  flex: 1;
`;

const DesignInfo = styled.div`
  text-align: center;
`;

const DesignName = styled.h3`
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const DesignDescription = styled.p`
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 10px;
`;

const DesignCategory = styled.span`
  background: ${props => {
    switch(props.category) {
      case 'traditional': return '#e8f4fd';
      case 'modern': return '#e8f5e8';
      case 'premium': return '#fff3cd';
      default: return '#f8f9fa';
    }
  }};
  color: ${props => {
    switch(props.category) {
      case 'traditional': return '#004085';
      case 'modern': return '#155724';
      case 'premium': return '#856404';
      default: return '#495057';
    }
  }};
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
`;

const SelectedBadge = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
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

const StructureSummary = styled.div`
  background: #e8f4fd;
  border: 1px solid #b8daff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
`;

const SummaryTitle = styled.h4`
  color: #004085;
  margin-bottom: 15px;
`;

const SummaryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
`;

const SummaryItem = styled.div`
  color: #004085;
`;

function DesignSelection({ structure, selectedDesign, onDesignSelect }) {
  const [designs, setDesigns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDesigns();
  }, []);

  // Проверяем, что structure существует
  if (!structure) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        <p>Структура книги не найдена. Сначала проанализируйте книгу.</p>
      </div>
    );
  }

  // Отладочная информация
  console.log('DesignSelection - structure:', structure);

  const loadDesigns = async () => {
    try {
      const response = await apiService.getAvailableDesigns();
      setDesigns(response.data.designs);
    } catch (error) {
      console.error('Ошибка загрузки дизайнов:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDesignPreview = (design) => {
    // Создаем превью на основе настроек дизайна
    const previews = {
      classic_islamic: {
        background: '#FFFFFF',
        titleColor: '#8B4513',
        headingColor: '#B8860B',
        textColor: '#2C2C2C',
        titleFont: 'serif',
        headingFont: 'serif',
        textFont: 'serif',
        titleSize: 16,
        headingSize: 12,
        textSize: 10
      },
      modern_minimal: {
        background: '#FFFFFF',
        titleColor: '#000000',
        headingColor: '#666666',
        textColor: '#333333',
        titleFont: 'sans-serif',
        headingFont: 'sans-serif',
        textFont: 'sans-serif',
        titleSize: 14,
        headingSize: 11,
        textSize: 9
      },
      dark_gold: {
        background: '#1A1A1A',
        titleColor: '#FFD700',
        headingColor: '#FFA500',
        textColor: '#E8E8E8',
        titleFont: 'serif',
        headingFont: 'serif',
        textFont: 'serif',
        titleSize: 15,
        headingSize: 11,
        textSize: 9
      }
    };

    return previews[design.name] || previews.classic_islamic;
  };

  const getCategoryLabel = (category) => {
    const labels = {
      traditional: 'Традиционный',
      modern: 'Современный',
      premium: 'Премиум'
    };
    return labels[category] || 'Стандартный';
  };

  if (loading) {
    return (
      <LoadingSpinner>
        <Spinner />
        <span style={{ marginLeft: '15px' }}>Загрузка дизайнов...</span>
      </LoadingSpinner>
    );
  }

  return (
    <div>
      <StructureSummary>
        <SummaryTitle>
          <Palette size={18} style={{ marginRight: '8px' }} />
          Структура книги
        </SummaryTitle>
        <SummaryGrid>
          <SummaryItem>
            <strong>Название:</strong> {structure?.title || 'Не указано'}
          </SummaryItem>
          <SummaryItem>
            <strong>Автор:</strong> {structure?.author || 'Не указано'}
          </SummaryItem>
          <SummaryItem>
            <strong>Всего страниц:</strong> {structure?.total_pages || 0}
          </SummaryItem>
          <SummaryItem>
            <strong>Разделов:</strong> {structure?.sections?.length || 0}
          </SummaryItem>
        </SummaryGrid>
      </StructureSummary>

      <h4 style={{ marginBottom: '20px', color: '#333' }}>
        Выберите дизайн для PDF файлов:
      </h4>

      <DesignGrid>
        {designs.map((design) => {
          const preview = getDesignPreview(design);
          const isSelected = selectedDesign === design.name;
          
          return (
            <DesignCard
              key={design.name}
              selected={isSelected}
              onClick={() => onDesignSelect(design.name)}
            >
              {isSelected && (
                <SelectedBadge>
                  <Check size={16} />
                </SelectedBadge>
              )}
              
              <DesignPreview $background={preview.background}>
                <PreviewContent>
                  <PreviewTitle
                    fontFamily={preview.titleFont}
                    fontSize={preview.titleSize}
                    color={preview.titleColor}
                  >
                    {design.display_name}
                  </PreviewTitle>
                  
                  <PreviewHeading
                    fontFamily={preview.headingFont}
                    fontSize={preview.headingSize}
                    color={preview.headingColor}
                  >
                    Кіріспе
                  </PreviewHeading>
                  
                  <PreviewText
                    fontFamily={preview.textFont}
                    fontSize={preview.textSize}
                    color={preview.textColor}
                  >
                    Бұл кітапта Алланың Елшісінің өмірі мен ізгіліктері туралы айтылады...
                  </PreviewText>
                </PreviewContent>
              </DesignPreview>

              <DesignInfo>
                <DesignName>
                  {design.display_name}
                  {design.name === 'classic_islamic' && (
                    <Star size={16} style={{ marginLeft: '8px', color: '#ffc107' }} />
                  )}
                </DesignName>
                <DesignDescription>
                  {design.description || 'Красивый дизайн для вашей книги'}
                </DesignDescription>
                <DesignCategory category={design.category}>
                  {getCategoryLabel(design.category)}
                </DesignCategory>
              </DesignInfo>
            </DesignCard>
          );
        })}
      </DesignGrid>

      {selectedDesign && (
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <button
            className="btn btn-primary"
            onClick={() => onDesignSelect(selectedDesign)}
          >
            Продолжить с выбранным дизайном
          </button>
        </div>
      )}

      <div style={{ marginTop: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '6px' }}>
        <h4 style={{ marginBottom: '10px', color: '#495057' }}>О дизайнах:</h4>
        <ul style={{ color: '#6c757d', lineHeight: '1.6' }}>
          <li><strong>Classic Islamic</strong> - традиционный исламский дизайн с золотыми акцентами</li>
          <li><strong>Modern Minimal</strong> - современный минималистичный стиль</li>
          <li><strong>Dark Gold</strong> - премиальный темный дизайн с золотыми элементами</li>
        </ul>
      </div>
    </div>
  );
}

export default DesignSelection;
