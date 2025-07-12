import React, { useState, useEffect } from "react";
import { fetchAnalyticsData } from "../../api/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  ComposedChart,
} from "recharts";
import {
  Calendar,
  TrendingUp,
  BookOpen,
  Clock,
  Target,
  Award,
  Heart,
  Brain,
  Moon,
  Zap,
  AlertTriangle,
  Users,
} from "lucide-react";

const AnalyticsPage = () => {
  const [selectedPeriod, setSelectedPeriod] = useState("7days");
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const data = await fetchAnalyticsData(selectedPeriod);
        setAnalyticsData(data);
      } catch (error) {
        console.error("Failed to fetch analytics data:", error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [selectedPeriod]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl font-semibold">Loading analytics...</div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl font-semibold text-red-500">
          Could not load analytics data.
        </div>
      </div>
    );
  }

  const {
    stats,
    weeklyData,
    moodDistribution,
    sleepQualityData,
    stressLevelData,
    correlationData,
    topicData,
  } = analyticsData;

  const getColorClasses = (color) => {
    const colorMap = {
      blue: "bg-blue-50 text-blue-600",
      green: "bg-green-50 text-green-600",
      purple: "bg-purple-50 text-purple-600",
      pink: "bg-pink-50 text-pink-600",
      indigo: "bg-indigo-50 text-indigo-600",
      orange: "bg-orange-50 text-orange-600",
    };
    return colorMap[color] || "bg-blue-50 text-blue-600";
  };

  const StatCard = ({
    icon: Icon,
    title,
    value,
    subtitle,
    trend,
    color = "blue",
  }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-lg ${getColorClasses(color)}`}>
          <Icon className="w-6 h-6" />
        </div>
        {trend && (
          <div
            className={`flex items-center text-sm ${
              trend > 0 ? "text-green-600" : "text-red-600"
            }`}
          >
            <TrendingUp className="w-4 h-4 mr-1" />
            {trend > 0 ? "+" : ""}
            {trend}%
          </div>
        )}
      </div>
      <div className="mt-4">
        <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
        <p className="text-sm text-gray-600 mt-1">{title}</p>
        {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
      </div>
    </div>
  );

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.dataKey}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Journal Analytics
          </h1>
          <p className="text-gray-600">
            Track your journaling journey and insights
          </p>

          {/* Period Selector */}
          <div className="flex gap-2 mt-4">
            {["7days", "30days", "90days", "1year"].map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedPeriod === period
                    ? "bg-blue-600 text-white"
                    : "bg-white text-gray-600 hover:bg-gray-50 border border-gray-200"
                }`}
              >
                {period === "7days" && "Last 7 Days"}
                {period === "30days" && "Last 30 Days"}
                {period === "90days" && "Last 90 Days"}
                {period === "1year" && "This Year"}
              </button>
            ))}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6 mb-8">
          <StatCard
            icon={BookOpen}
            title="Total Entries"
            value={stats.totalEntries}
            subtitle="Since you started"
            color="blue"
          />
          <StatCard
            icon={Target}
            title="Current Streak"
            value={`${stats.currentStreak} days`}
            subtitle={`Longest: ${stats.longestStreak} days`}
            color="green"
          />
          <StatCard
            icon={Clock}
            title="Avg. Words per Entry"
            value={stats.averageWords}
            subtitle={`${stats.totalWords.toLocaleString()} total words`}
            color="purple"
          />
          <StatCard
            icon={Heart}
            title="Average Mood"
            value={stats.averageMood}
            subtitle="Out of 10"
            trend={stats.weeklyGrowth}
            color="pink"
          />
          <StatCard
            icon={Moon}
            title="Sleep Quality"
            value={stats.averageSleep}
            subtitle="Average (1-5)"
            trend={stats.sleepTrend}
            color="indigo"
          />
          <StatCard
            icon={Zap}
            title="Stress Level"
            value={stats.averageStress}
            subtitle="Out of 10"
            trend={stats.stressTrend}
            color="orange"
          />
          <StatCard
            icon={Users}
            title="Social Engagement"
            value={stats.averageSocial}
            subtitle="Average (1-5)"
            trend={stats.socialTrend}
            color="teal"
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Writing Activity Chart */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Writing Activity
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="day" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="entries" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Sleep & Stress Trend Chart */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Sleep Quality & Stress Levels
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="day" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip content={<CustomTooltip />} />
                <Bar
                  dataKey="stress"
                  fill="#f97316"
                  radius={[4, 4, 0, 0]}
                  opacity={0.7}
                />
                <Line
                  type="monotone"
                  dataKey="sleep"
                  stroke="#6366f1"
                  strokeWidth={3}
                  dot={{ fill: "#6366f1", strokeWidth: 2, r: 4 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
            <div className="flex items-center justify-center gap-6 mt-4">
              <div className="flex items-center text-sm">
                <div className="w-3 h-3 bg-indigo-500 rounded-full mr-2"></div>
                <span className="text-gray-600">Sleep Quality (hours)</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
                <span className="text-gray-600">Stress Level (1-10)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Sleep-Happiness Correlation */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Sleep Quality vs Happiness Correlation
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <ResponsiveContainer width="100%" height={300}>
                <ScatterChart data={correlationData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="sleep"
                    stroke="#64748b"
                    label={{
                      value: "Sleep Quality (hours)",
                      position: "insideBottom",
                      offset: -5,
                    }}
                  />
                  <YAxis
                    stroke="#64748b"
                    label={{
                      value: "Happiness Level",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                            <p className="font-medium text-gray-900">
                              Sleep-Happiness Data
                            </p>
                            <p className="text-sm text-blue-600">
                              Sleep: {data.sleep}h
                            </p>
                            <p className="text-sm text-green-600">
                              Happiness: {data.happiness}/10
                            </p>
                            <p className="text-sm text-orange-600">
                              Stress: {data.stress}/10
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Scatter dataKey="happiness" fill="#10b981" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="flex items-center mb-2">
                  <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
                  <span className="font-medium text-green-800">
                    Strong Correlation
                  </span>
                </div>
                <p className="text-sm text-green-700">
                  Better sleep quality strongly correlates with higher happiness
                  levels (r = 0.84)
                </p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center mb-2">
                  <Moon className="w-5 h-5 text-blue-600 mr-2" />
                  <span className="font-medium text-blue-800">
                    Optimal Sleep
                  </span>
                </div>
                <p className="text-sm text-blue-700">
                  Your happiest days occur when you get 7.5-8.5 hours of sleep
                </p>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <div className="flex items-center mb-2">
                  <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
                  <span className="font-medium text-orange-800">
                    Sleep Deficit
                  </span>
                </div>
                <p className="text-sm text-orange-700">
                  Less than 6 hours of sleep significantly impacts your mood and
                  stress levels
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Mood Trend Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Mood Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="day" stroke="#64748b" />
              <YAxis domain={[0, 10]} stroke="#64748b" />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="mood"
                stroke="#10b981"
                strokeWidth={3}
                dot={{ fill: "#10b981", strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Additional Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Mood Distribution */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Mood Distribution
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={moodDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {moodDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {moodDistribution.map((item, index) => (
                <div key={index} className="flex items-center text-xs">
                  <div
                    className="w-2 h-2 rounded-full mr-2"
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-gray-600">
                    {item.name}: {item.value}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Sleep Quality Distribution */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Sleep Quality
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={sleepQualityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sleepQualityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {sleepQualityData.map((item, index) => (
                <div key={index} className="flex items-center text-xs">
                  <div
                    className="w-2 h-2 rounded-full mr-2"
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-gray-600">
                    {item.quality}: {item.value}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Stress Level Distribution */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Stress Levels
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={stressLevelData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {stressLevelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {stressLevelData.map((item, index) => (
                <div key={index} className="flex items-center text-xs">
                  <div
                    className="w-2 h-2 rounded-full mr-2"
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-gray-600">
                    {item.level}: {item.value}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Top Topics */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Most Written Topics
            </h3>
            <div className="space-y-3">
              {topicData.map((topic, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div
                      className="w-3 h-3 rounded-full mr-3"
                      style={{ backgroundColor: topic.color }}
                    ></div>
                    <span className="text-gray-700 text-sm">{topic.topic}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {topic.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Insights Section */}
        <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            AI-Generated Insights
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analyticsData.insights &&
              analyticsData.insights.map((insight, index) => (
                <div
                  key={index}
                  className="p-4 bg-blue-50 rounded-lg text-sm text-blue-800"
                >
                  {insight}
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
