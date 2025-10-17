import React, { useState } from 'react';
import styled from 'styled-components';
import { Upload, FileText, Download, Settings } from 'lucide-react';
import FileUpload from './components/FileUpload';
import StructureAnalysis from './components/StructureAnalysis';
import DesignSelection from './components/DesignSelection';
import PDFGeneration from './components/PDFGeneration';
import { apiService } from './services/apiService';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 40px;
  color: white;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  opacity: 0.9;
`;

const MainContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const StepContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 30px;
  margin-bottom: 20px;
`;

const StepHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
`;

const StepIcon = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: ${props => props.$active ? '#007bff' : '#e9ecef'};
  color: ${props => props.$active ? 'white' : '#6c757d'};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-weight: bold;
  font-size: 1.2rem;
`;

const StepTitle = styled.h2`
  color: ${props => props.$active ? '#007bff' : '#6c757d'};
  margin: 0;
`;

const StatusBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  color: ${props => props.$completed ? '#28a745' : props.$active ? '#007bff' : '#6c757d'};
  font-weight: 500;
`;

const StatusIcon = styled.div`
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: ${props => props.$completed ? '#28a745' : props.$active ? '#007bff' : '#e9ecef'};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-size: 0.9rem;
`;

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [bookData, setBookData] = useState(null);
  const [structure, setStructure] = useState(null);
  const [selectedDesign, setSelectedDesign] = useState('classic_islamic');
  const [generatedFiles, setGeneratedFiles] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const steps = [
    { id: 1, title: 'Загрузка книги', icon: Upload, completed: !!bookData },
    { id: 2, title: 'Анализ структуры', icon: FileText, completed: !!structure },
    { id: 3, title: 'Выбор дизайна', icon: Settings, completed: !!selectedDesign },
    { id: 4, title: 'Генерация PDF', icon: Download, completed: !!generatedFiles }
  ];

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiService.uploadBook(formData);
      setBookData(response.data);
      setCurrentStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке файла');
    } finally {
      setLoading(false);
    }
  };

  const handleStructureAnalysis = async (splitMode = 'by_headings') => {
    if (!bookData) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.analyzeStructure(bookData.book_id, splitMode);
      console.log('API Response:', response.data);
      // Устанавливаем только структуру из ответа
      setStructure(response.data.structure || response.data);
      setCurrentStep(3);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при анализе структуры');
    } finally {
      setLoading(false);
    }
  };

  const handleDesignSelection = (design) => {
    setSelectedDesign(design);
    setCurrentStep(4);
  };

  const handlePDFGeneration = async () => {
    if (!bookData || !structure) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.generatePDFs(bookData.book_id, selectedDesign);
      setGeneratedFiles(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при генерации PDF');
    } finally {
      setLoading(false);
    }
  };

  const resetProcess = () => {
    setCurrentStep(1);
    setBookData(null);
    setStructure(null);
    setSelectedDesign('classic_islamic');
    setGeneratedFiles(null);
    setError(null);
  };

  return (
    <AppContainer>
      <Header>
        <Title>AI Book Splitter & Designer</Title>
        <Subtitle>Автоматическое разделение книг на разделы с красивым дизайном</Subtitle>
      </Header>

      <MainContent>
        <StatusBar>
          {steps.map((step) => {
            const Icon = step.icon;
            const isActive = currentStep === step.id;
            const isCompleted = step.completed;
            
            return (
              <StatusItem key={step.id} $completed={isCompleted} $active={isActive}>
                <StatusIcon $completed={isCompleted} $active={isActive}>
                  {isCompleted ? '✓' : <Icon size={16} />}
                </StatusIcon>
                {step.title}
              </StatusItem>
            );
          })}
        </StatusBar>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {currentStep === 1 && (
          <StepContainer>
            <StepHeader>
              <StepIcon $active={true}>1</StepIcon>
              <StepTitle $active={true}>Загрузка книги</StepTitle>
            </StepHeader>
            <FileUpload 
              onFileUpload={handleFileUpload}
              loading={loading}
              acceptedFormats={['.pdf', '.docx', '.epub']}
            />
          </StepContainer>
        )}

        {currentStep === 2 && bookData && (
          <StepContainer>
            <StepHeader>
              <StepIcon $active={true}>2</StepIcon>
              <StepTitle $active={true}>Анализ структуры</StepTitle>
            </StepHeader>
            <StructureAnalysis 
              bookData={bookData}
              onAnalyze={handleStructureAnalysis}
              loading={loading}
            />
          </StepContainer>
        )}

        {currentStep === 3 && structure && (
          <StepContainer>
            <StepHeader>
              <StepIcon $active={true}>3</StepIcon>
              <StepTitle $active={true}>Выбор дизайна</StepTitle>
            </StepHeader>
            <DesignSelection 
              structure={structure}
              selectedDesign={selectedDesign}
              onDesignSelect={handleDesignSelection}
            />
          </StepContainer>
        )}

        {currentStep === 4 && structure && (
          <StepContainer>
            <StepHeader>
              <StepIcon $active={true}>4</StepIcon>
              <StepTitle $active={true}>Генерация PDF</StepTitle>
            </StepHeader>
            <PDFGeneration 
              structure={structure}
              selectedDesign={selectedDesign}
              onGenerate={handlePDFGeneration}
              generatedFiles={generatedFiles}
              loading={loading}
            />
          </StepContainer>
        )}

        {generatedFiles && (
          <div className="text-center mt-4">
            <button 
              className="btn btn-secondary"
              onClick={resetProcess}
            >
              Обработать новую книгу
            </button>
          </div>
        )}
      </MainContent>
    </AppContainer>
  );
}

export default App;
