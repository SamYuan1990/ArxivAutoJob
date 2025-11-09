import { useState, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
//import * as THREE from 'three';
import './App.css';

// 数据解析和转换函数
const parseData = (csvData) => {
  return csvData.map(row => {
    // 处理多值情况
    const positionIndices = row.position_index.includes('_') 
      ? row.position_index.split('_') 
      : [row.position_index];
    
    const initiativeIndices = row.initiative_index.includes('_')
      ? row.initiative_index.split('_')
      : [row.initiative_index];

    // 为每个组合创建数据点
    const points = [];
    positionIndices.forEach(pos => {
      initiativeIndices.forEach(init => {
        points.push({
          arxiv_id: row.arxiv_id,
          title: row.title,
          date: new Date(row.date),
          position_index: pos.trim(),
          initiative_index: init.trim(),
          downloaded: row.downloaded === 'true'
        });
      });
    });

    return points;
  }).flat();
};

// 坐标映射函数
const mapDateToX = (date, minDate, maxDate) => {
  const timeRange = maxDate - minDate;
  return ((date - minDate) / timeRange) * 20 - 10; // 映射到 -10 到 10
};

const mapPositionToY = (position) => {
  const positionMap = {
    'training': -4,
    'post training': -1,
    'prompt': 2,
    'external data mgr': 5,
    'multiple agents': 8
  };
  return positionMap[position] || 0;
};

const mapInitiativeToZ = (initiative) => {
  const initiativeMap = {
    'hard code style': -4,
    'code impls': -1,
    'auto adjust according to specific metric': 2,
    'auto adjust leave to LLM': 5
  };
  return initiativeMap[initiative] || 0;
};

// 3D 数据点组件
const DataPoint = ({ data, onClick, selected }) => {
  const meshRef = useRef();
  
  const color = data.downloaded ? '#ff6b6b' : '#4ecdc4';
  const scale = selected ? 1.5 : 1;

  return (
    <mesh 
      ref={meshRef}
      position={[data.x, data.y, data.z]}
      scale={scale}
      onClick={(e) => {
        e.stopPropagation();
        onClick(data);
      }}
    >
      <sphereGeometry args={[0.2, 16, 16]} />
      <meshStandardMaterial color={color} />
    </mesh>
  );
};

// 坐标轴组件
const Axes = ({ minDate, maxDate }) => {
  return (
    <group>
      {/* X轴 - 日期 */}
      <mesh position={[0, -6, 0]}>
        <boxGeometry args={[20, 0.05, 0.05]} />
        <meshStandardMaterial color="#666" />
      </mesh>
      
      {/* Y轴 - Position Index */}
      <mesh position={[-10, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
        <boxGeometry args={[12, 0.05, 0.05]} />
        <meshStandardMaterial color="#666" />
      </mesh>
      
      {/* Z轴 - Initiative Index */}
      <mesh position={[-10, -6, 0]} rotation={[0, Math.PI / 2, 0]}>
        <boxGeometry args={[10, 0.05, 0.05]} />
        <meshStandardMaterial color="#666" />
      </mesh>

      {/* 刻度标签 */}
      <AxisLabels minDate={minDate} maxDate={maxDate} />
    </group>
  );
};

const AxisLabels = ({ minDate, maxDate }) => {
  const formatDate = (date) => {
    return date.toISOString().split('T')[0];
  };

  return (
    <group>
      {/* X轴标签 */}
      {[-10, -5, 0, 5, 10].map((x, i) => {
        const date = new Date(minDate.getTime() + (i / 4) * (maxDate - minDate));
        return (
          <Text
            key={i}
            position={[x, -7, 0]}
            fontSize={0.3}
            color="#333"
            anchorX="center"
            anchorY="middle"
          >
            {formatDate(date)}
          </Text>
        );
      })}

      {/* Y轴标签 */}
      {[
        { label: 'Training', y: -4 },
        { label: 'Post Training', y: -1 },
        { label: 'Prompt', y: 2 },
        { label: 'External Data Mgr', y: 5 },
        { label: 'Multiple Agents', y: 8 }
      ].map((item, i) => (
        <Text
          key={i}
          position={[-11.5, item.y, 0]}
          fontSize={0.3}
          color="#333"
          anchorX="center"
          anchorY="middle"
          rotation={[0, 0, Math.PI / 2]}
        >
          {item.label}
        </Text>
      ))}

      {/* Z轴标签 */}
      {[
        { label: 'Hard Code', z: -4 },
        { label: 'Code Impls', z: -1 },
        { label: 'Auto Adjust Metric', z: 2 },
        { label: 'Auto Adjust LLM', z: 5 }
      ].map((item, i) => (
        <Text
          key={i}
          position={[-10, -7, item.z]}
          fontSize={0.3}
          color="#333"
          anchorX="center"
          anchorY="middle"
          rotation={[0, Math.PI / 2, 0]}
        >
          {item.label}
        </Text>
      ))}

      {/* 轴标题 */}
      <Text position={[0, -8, 0]} fontSize={0.4} color="#333" anchorX="center">
        Date
      </Text>
      <Text position={[-13, 1, 0]} fontSize={0.4} color="#333" anchorX="center" rotation={[0, 0, Math.PI / 2]}>
        Position Index
      </Text>
      <Text position={[-10, -8, 3]} fontSize={0.4} color="#333" anchorX="center" rotation={[0, Math.PI / 2, 0]}>
        Initiative Index
      </Text>
    </group>
  );
};

// 主组件
function App() {
  const [data, setData] = useState([]);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // 处理文件上传
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsLoading(true);
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const csvText = e.target.result;
      const rows = csvText.split('\n').slice(1); // 跳过表头
      
      const parsedData = rows.map(row => {
        const columns = row.split(',');
        if (columns.length >= 7) {
          return {
            arxiv_id: columns[0],
            date: columns[1],
            title: columns[2],
            position_index: columns[3],
            initiative_index: columns[4],
            position_index_comments: columns[5],
            initiative_index_comments: columns[6],
            downloaded: columns[7] || 'false'
          };
        }
        return null;
      }).filter(Boolean);

      // 转换数据
      const transformedData = parseData(parsedData);
      
      // 计算日期范围
      const dates = transformedData.map(d => d.date);
      const minDate = new Date(Math.min(...dates));
      const maxDate = new Date(Math.max(...dates));

      // 映射坐标
      const dataWithCoords = transformedData.map(point => ({
        ...point,
        x: mapDateToX(point.date, minDate, maxDate),
        y: mapPositionToY(point.position_index),
        z: mapInitiativeToZ(point.initiative_index)
      }));

      setData(dataWithCoords);
      setIsLoading(false);
    };

    reader.readAsText(file);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>arXiv Papers 3D Visualization</h1>
        <div className="file-upload">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            className="file-input"
          />
          {isLoading && <div className="loading">Loading...</div>}
        </div>
      </header>

      <div className="visualization-container">
        <div className="canvas-container">
          <Canvas camera={{ position: [15, 10, 15], fov: 50 }}>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} />
            
            {data.length > 0 && (
              <>
                <Axes 
                  minDate={new Date(Math.min(...data.map(d => d.date)))}
                  maxDate={new Date(Math.max(...data.map(d => d.date)))}
                />
                
                {data.map((point, index) => (
                  <DataPoint
                    key={index}
                    data={point}
                    onClick={setSelectedPoint}
                    selected={selectedPoint === point}
                  />
                ))}
              </>
            )}
            
            <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
          </Canvas>
        </div>

        {selectedPoint && (
          <div className="details-panel">
            <h3>Paper Details</h3>
            <div className="detail-item">
              <strong>arXiv ID:</strong> {selectedPoint.arxiv_id}
            </div>
            <div className="detail-item">
              <strong>Title:</strong> {selectedPoint.title}
            </div>
            <div className="detail-item">
              <strong>Date:</strong> {selectedPoint.date.toDateString()}
            </div>
            <div className="detail-item">
              <strong>Position Index:</strong> {selectedPoint.position_index}
            </div>
            <div className="detail-item">
              <strong>Initiative Index:</strong> {selectedPoint.initiative_index}
            </div>
            <div className="detail-item">
              <strong>Downloaded:</strong> {selectedPoint.downloaded ? 'Yes' : 'No'}
            </div>
            <button 
              className="close-btn"
              onClick={() => setSelectedPoint(null)}
            >
              Close
            </button>
          </div>
        )}
      </div>

      {data.length === 0 && !isLoading && (
        <div className="placeholder">
          <p>Please upload a CSV file to visualize the data</p>
          <p>Expected CSV format: arxiv_id,date,title,position_index,initiative_index,position_index_comments,initiative_index_comments,downloaded</p>
        </div>
      )}
    </div>
  );
}

export default App;