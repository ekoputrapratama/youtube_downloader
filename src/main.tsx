import ReactDOM from "react-dom/client";
import GlobalStyles from '@mui/material/GlobalStyles';
import App from "./App.tsx";
import "./styles/tailwind.css";
import "./common/i18n";

const rootElement = document.querySelector("#root") as Element;
if (!rootElement.innerHTML) {
	const root = ReactDOM.createRoot(rootElement);
	root.render(
    <>
      <GlobalStyles styles="@layer theme, base, mui, components, utilities" />
      <App />
    </>
		
	);
}
