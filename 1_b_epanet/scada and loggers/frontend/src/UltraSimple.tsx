import React from 'react';

const UltraSimple: React.FC = () => {
  return React.createElement('div', {
    style: { padding: '20px', backgroundColor: 'lightblue' }
  }, 'Ultra Simple React Test - If you see this, React works!');
};

export default UltraSimple;
