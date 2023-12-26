import SvgIcon, { SvgIconProps } from '@mui/material/SvgIcon';

const FileIcon = (props: SvgIconProps) => {
  return (
    <SvgIcon {...props} viewBox="0 0 24 24">
      <g>
        <path
          fill="#303C42"
          d="M22,3H2C0.8969727,3,0,3.8969727,0,5v14c0,1.1030273,0.8969727,2,2,2h20c1.1030273,0,2-0.8969727,2-2V5
		C24,3.8969727,23.1030273,3,22,3z"
        />
        <path
          fill="#57C1EF"
          d="M1,5c0-0.5512695,0.4487305-1,1-1h20c0.5512695,0,1,0.4487305,1,1v12.2929688l-7.6464844-7.6464844
		c-0.1953125-0.1953125-0.5117188-0.1953125-0.7070313,0L8.5,15.7929688l-2.1464844-2.1464844
		c-0.1953125-0.1953125-0.5117188-0.1953125-0.7070313,0L1,18.2929688V5z"
        />
        <path
          fill="#7CB342"
          d="M22,20H2c-0.3514404,0-0.6463623-0.1931152-0.8247681-0.4682007L6,14.7070313l3.1464844,3.1464844
		c0.1953125,0.1953125,0.5117188,0.1953125,0.7070313,0s0.1953125-0.5117188,0-0.7070313L9.2070313,16.5L15,10.7070313l8,8V19
		C23,19.5512695,22.5512695,20,22,20z"
        />
        <path
          opacity="0.1"
          fill="#010101"
          d="M22.6367188,18.34375c-0.1801758,0.2644043-0.468689,0.4492188-0.8119507,0.4492188
		H1.9140625l-0.7388306,0.7388306C1.3536377,19.8068848,1.6485596,20,2,20h20c0.5512695,0,1-0.4487305,1-1v-0.2929688
		L22.6367188,18.34375z"
        />
        <circle fill="#303C42" cx="8" cy="9" r="3" />
        <circle fill="#FFCB29" cx="8" cy="9" r="2" />
        <polygon
          opacity="0.1"
          fill="#010101"
          points="14.979187,10.7278442 17.2815552,12.9885864 15,10.7070313 	"
        />
        <linearGradient
          id="SVGID_1_"
          gradientUnits="userSpaceOnUse"
          x1="-0.7076802"
          y1="6.0743113"
          x2="24.7076797"
          y2="17.9256878"
        >
          <stop offset="0" stopColor="#FFFFFF" stopOpacity={0.2} />
          <stop offset="1" stopColor="#FFFFFF" stopOpacity={0.2} />
        </linearGradient>
        <path
          fill="url(#SVGID_1_)"
          d="M22,3H2C0.8969727,3,0,3.8969727,0,5v14c0,1.1030273,0.8969727,2,2,2h20
		c1.1030273,0,2-0.8969727,2-2V5C24,3.8969727,23.1030273,3,22,3z"
        />
      </g>
    </SvgIcon>
  );
};

export default FileIcon;
