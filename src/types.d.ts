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
	interface DownloadQueue {
		onProgress: { connect: (callback: DownloadQueueCallback) => void };
		start: () => Promise<any>;
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

		download: (queueItem: string) => Promise<DownloadQueue>;

		downloadAll: (queueItems: Array<string>) => Promise<any>;
	};

	/**
	 * Adds a custom property to the standard Window interface (for browser environments).
	 */
	// interface Window {
	// myCustomFunction: (arg: string) => void;
	// }
}
