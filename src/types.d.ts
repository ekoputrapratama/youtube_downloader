/* eslint-disable @typescript-eslint/no-explicit-any */
// src/types/globals.d.ts

// This makes the file a module, so we can use declare global
export {};

declare global {
	type FileType = "audio" | "video";

	interface DownloadQueueItem {
		type: FileType;
		format: string;
		noPlaylist: boolean;
		url: string;
	}
	type DownloadQueueCallback = (jsonString: string) => void;
	type FfmpegDownloadCallback = (path: string) => void;
	interface DownloadQueue {
		onProgress: { connect: (callback: DownloadQueueCallback) => void };
		start: () => Promise<any>;
	}
	interface FfmpegDownloader {
		onFinished: { connect: (callback: FfmpegDownloadCallback) => void };
	}
	interface DownloadProgress {
		id: number;
		status: string;
		percentage: number;
	}
	/**
	 * A global variable for initial application data.
	 */
	declare var YTDLP: {
		getTitle: (url: string) => Promise<string>;

		download: (queueItem: string, options: string) => Promise<DownloadQueue>;

		downloadAll: (queueItems: Array<string>) => Promise<any>;
		openUrl: (url: string) => Promise<any>;
		getDefaultDownloadDirectory: () => Promise<string>;
		selectDirectory: () => Promise<string>;
		initializeFfmpeg: () => Promise<FfmpegDownloader>;
	};

	/**
	 * Adds a custom property to the standard Window interface (for browser environments).
	 */
	// interface Window {
	// myCustomFunction: (arg: string) => void;
	// }
}
