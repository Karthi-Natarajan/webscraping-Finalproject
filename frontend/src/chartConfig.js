// chartConfig.js
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend
} from "chart.js";

// Register all required elements / scales
ChartJS.register(
  ArcElement,      // Pie chart
  BarElement,      // Bar chart
  LineElement,     // Line chart
  PointElement,    // Line points
  CategoryScale,   // X axis
  LinearScale,     // Y axis
  TimeScale,
  Tooltip,
  Legend
);

export default ChartJS;
